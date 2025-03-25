from nicegui import app, ui
import requests
import yarl
from utils import *
from functools import partial


class VappPage:
    def __init__(self): ...

    def render(self):
        with ui.row().classes("w-full justify-between items-center mt-4"):
            ui.markdown("# Proxmox Pools Manager")
            node_list = get_all_node_names()
            node_selector = ui.select(node_list).classes("w-full flex-1")
            self.currently_selected_node = node_selector.value
            ui.button("Logout", on_click=lambda: ui.navigate.to("/logout"))
        ui.separator()

        with ui.expansion(
            "Create Vapp",
            icon="work",
            caption="Create a Vapp from current VM's",
        ).classes("w-full"):
            vcw = VappCreatorView(node_name=self.currently_selected_node)
            vcw.render()

        ui.separator()

        with ui.expansion(
            "Templates",
            icon="work",
            caption="Templates that can be tunred into active Pools",
        ).classes("w-full"):
            self.render_templates()

        ui.separator()

        with ui.expansion(
            "Active Pools",
            icon="work",
            caption="Active pools/Labs that have been cloned",
        ).classes("w-full"):
            self.render_active_pools()

    def render_templates(self):
        try:
            # note, this is not final. maybe have some tempalte cards, then a list of
            # current vapps
            ui.markdown("## Templates")

            for i in range(1, 3):
                with ui.card().classes("w-full border"):
                    with ui.row().classes(
                        "w-full justify-between items-center mt-4 flex-1"
                    ):
                        ui.input("Pool Name").classes("flex-1")
                        ui.checkbox("Start Pool post clone").classes("flex-1")

                        ui.button("Clone").classes("flex-1")

            proxmox_class = get_proxmox_class()

            # for node in proxmox_class.nodes.get():
            #     # print(node)
            #     for vm in proxmox_class.nodes(node["node"]).qemu.get():
            #         ui.label(f"{vm['vmid']}. {vm['name']} => {vm['status']}")

            # ui.markdown("## Templates")

            # for pool in proxmox_class.pools.get():
            #     with ui.card().classes("w-full") as card:
            #         ui.markdown(f'### {pool.get("poolid")}')
            #         ui.label(pool.get("comment"))

            #         # Flex container for buttons spread out evenly
            #         with ui.row().classes(
            #             "w-full justify-between items-center mt-4 flex-1"
            #         ):
            #             ui.button("Start").classes("w-full flex-1")
            #             ui.button("Stop").classes("w-full flex-1")
            #             ui.button("Restart").classes("w-full flex-1")
            #             ui.button("Delete").classes("w-full flex-1")
            #             select1 = ui.select(
            #                 ["snapshot1", "snapshot2", "snapshot3"], value="snapshot1"
            #             ).classes("border")
            #             ui.button("< Revert to snapshot").classes("w-full flex-1")

        except Exception as e:
            print(e)
            ui.notify(f"Error occured: {e}", position="top-right", type="warning")

    def render_active_pools(self):
        try:
            # note, this is not final. maybe have some tempalte cards, then a list of
            # current vapps
            # for i in range(1, 3):
            #     with ui.card().classes("w-full"):
            #         ui.button("Start")
            #         ui.button("Stop")
            #         ui.button("Clone")

            proxmox_class = get_proxmox_class()

            # for node in proxmox_class.nodes.get():
            #     # print(node)
            #     for vm in proxmox_class.nodes(node["node"]).qemu.get():
            #         ui.label(f"{vm['vmid']}. {vm['name']} => {vm['status']}")

            ui.markdown("## Active Vapps")

            for pool in proxmox_class.pools.get():
                pool_name = pool.get("poolid")
                vm_ids_in_pool = get_all_vms_in_pool(pool_name=pool_name)
                with ui.card().classes("w-full border") as card:
                    ui.markdown(f"### {pool_name}")
                    ui.label(pool.get("comment"))

                    # Flex container for buttons spread out evenly
                    with ui.row().classes(
                        "w-full justify-between items-center mt-4 flex-1"
                    ):
                        # stop_all_vms_in_pool
                        ui.button(
                            "Start", on_click=partial(get_all_vms_in_pool, pool_name)
                        ).classes("w-full flex-1")
                        ui.button("Stop").classes("w-full flex-1")
                        # restart_all_vms_in_pool
                        ui.button("Restart").classes("w-full flex-1")
                        # delete_all_resources_in_pool (nic, VM's, etc)
                        ui.button("Delete").classes("w-full flex-1")
                        select1 = ui.select(
                            ["snapshot1", "snapshot2", "snapshot3"], value="snapshot1"
                        ).classes("border")
                        ui.button("< Revert to snapshot").classes("w-full flex-1")

                        ui.separator()

                        with ui.expansion("VM's in pool:").classes("w-full"):
                            for vmid in vm_ids_in_pool:
                                with ui.row().classes(
                                    "w-full justify-between items-center mt-4 "
                                ):
                                    ui.label(get_vm_name(vmid))
                                    ui.button("Start", on_click=partial(start_vm, vmid))
                                    ui.button("Stop", on_click=partial(stop_vm, vmid))
                                    ui.button(
                                        "Restart", on_click=partial(restart_vm, vmid)
                                    )
                                    ui.separator()
        except Exception as e:
            print(e)
            ui.notify(f"Error occured: {e}", position="top-right", type="warning")

    def start_all_vms_in_pool(self, vm_ids):
        """

        Starts all VM's in pool
        """

        """
            for vm in vm_pool:
                start_vm(vm.vmid)
        """


class VappCreatorView:
    def __init__(self, node_name):
        self.node_name = node_name

    def render(self):
        ui.label("vapp creator")
        self.create_stepper()

    def create_stepper(self):
        proxmox_class = get_proxmox_class()
        raw_vm_data = get_all_vms(self.node_name)

        with ui.stepper().props("vertical").classes("w-full") as stepper:
            print(raw_vm_data)
            with ui.step("Select VM's"):
                self.vm_table = ui.aggrid(
                    {
                        "columnDefs": [
                            {
                                "headerName": "",
                                "checkboxSelection": True,
                                "headerCheckboxSelection": True,
                                "width": 30,
                                "pinned": "left",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "VM Name",
                                "field": "name",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            {
                                "headerName": "VM ID",
                                "field": "vmid",
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                            },
                            # {
                            #     "headerName": "Node",
                            #     "field": "node",
                            #     "filter": "agTextColumnFilter",
                            #     "floatingFilter": True,
                            # },
                        ],
                        "rowData": raw_vm_data,
                        "enableCellTextSelection": True,  # allows selecting data
                        "rowSelection": "multiple",
                    }
                ).classes(f"w-full")

                ui.separator()
                with ui.stepper_navigation():
                    ui.button("Next", on_click=stepper.next)
                    ui.button("Back", on_click=stepper.previous)

            with ui.step("Enter Vapp/Pool Name"):
                with ui.row().classes(
                    "w-full justify-between items-center mt-4 flex-1"
                ):
                    # ui.label(get_vm_name(vmid))
                    self.vapp_name = ui.input("Template Name").classes("w-full flex-1")
                    ui.separator()
                    with ui.stepper_navigation():
                        ui.button("Next", on_click=stepper.next)
                        ui.button("Back", on_click=stepper.previous)

            # waiting on this, this is extra steps/complexity
            # with ui.step("Select Node to deploy to"):
            #     '''
            #     Allowing user to select the node INSTEAD of auto-deploying to the same node
            #     allows for deploying to go to any node.

            #     May hit issues with the WAN on the FW?
            #     '''
            #     #ui.label("")
            #     with ui.row().classes(
            #         "w-full justify-between items-center mt-4 flex-1"
            #     ):
            #         # list of nodes - use a call to get this list
            #         nodes = get_all_node_names()
            #         self.node_name = ui.select(nodes).classes("w-full")
            #         ui.separator()
            #         with ui.stepper_navigation():
            #             ui.button("Next", on_click=stepper.next)
            #             ui.button("Back", on_click=stepper.previous)

            with ui.step("Create Vapp/Pool"):
                ui.checkbox("start VAPP/Pool on creation")
                ui.button(
                    "Create Template from Selected VM's", on_click=self._create_template
                ).classes("w-full flex-1")
                with ui.stepper_navigation():
                    ui.button("Back", on_click=stepper.previous)

    async def _create_template(self):
        """
        Creates template(s) for live vm

        1. Clone VM
        2. Template said clone
        3.

        Current Reqs: All VM's need to be on the same host due to the req of a node name for NIC's
         - wait on that, could have a "which node" to put on, would probably work best to do this
         - need to double check this, aparently pools are datacenter wide
        """
        selected_rows = await self.vm_table.get_selected_rows()
        vm_ids = []

        vapp_name = (self.vapp_name.value).upper()

        ui.notify(f"Creating VAPP: {vapp_name}", position="top-right")

        for row in selected_rows:
            print(row)
            # toss all id's in their own list
            vm_ids.append(row.get("vmid"))
            # ui.notify(
            #     f'Adding cloned {row.get("name")} to vapp {self.vapp_name.value}',
            #     position="top-right",
            # )

        # create a NIC, ex: "POOLNAME-NIC"
        # https://pve.proxmox.com/pve-docs/api-viewer/index.html#/nodes/{node}/network
        create_nic(
            iface_name=f"PPM_{vapp_name}_NIC",
            node="proxmox",  # user input for which node to clone to
            type="bridge",
        )

        # Clone hosts
        # for i in hosts, clone
