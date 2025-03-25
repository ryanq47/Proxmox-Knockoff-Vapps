from nicegui import app, ui
import requests
import yarl
from utils import *
from functools import partial

# Ryan todo: Move calls to take a node name. instead of iterating


class VappPage:
    def __init__(self):
        self.currently_selected_node = None

    def render(self):
        with ui.row().classes("w-full justify-between items-center mt-4"):
            ui.markdown("# Proxmox Pools Manager")
            node_list = get_all_node_names()
            self.currently_selected_node = ui.select(
                node_list,
                on_change=self.on_node_changed,
                # value=node_list[0],  # default first node
            ).classes("w-full flex-1")
            ui.button("Logout", on_click=lambda: ui.navigate.to("/logout"))

        # Vapp Creator section (node dependent)
        self.vapp_creator_container = ui.column().classes("w-full")
        with self.vapp_creator_container:
            vcw = VappCreatorView(node_name=self.currently_selected_node.value)
            vcw.render()

        # Templates section using the TemplatesView class

        self.templates_container = ui.column().classes("w-full")
        with self.templates_container:
            TemplatesView().render()

        # Active Pools section using the ActivePoolsView class

        self.active_pools_container = ui.column().classes("w-full")
        with self.active_pools_container:
            ActivePoolsView().render()

    def on_node_changed(self):
        # Update node-dependent sections without duplicating the expansion blocks.
        self.vapp_creator_container.clear()
        vcw = VappCreatorView(node_name=self.currently_selected_node.value)
        vcw.render()

        self.templates_container.clear()
        TemplatesView().render()

        self.active_pools_container.clear()
        ActivePoolsView().render()


class VappCreatorView:
    def __init__(self, node_name):
        self.node_name = node_name

    def render(self):
        with ui.expansion("Vapp Creator", icon="work", caption="Create Vapps").classes(
            "w-full"
        ):
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

            with ui.step("Enter Vapp template Name"):
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
        try:
            selected_rows = await self.vm_table.get_selected_rows()
            vm_ids = []

            vapp_name = (self.vapp_name.value).upper()

            ui.notify(f"Creating VAPP Template: {vapp_name}", position="top-right")

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
                node=self.node_name,  # user input for which node to clone to
                type="bridge",
            )

            # Create template pool,
            template_pool_name = f"PPM_TEMPLATE_{vapp_name}"
            create_pool(poolid=template_pool_name)

            new_vm_ids = []
            # clone hosts needed
            # for host in selected_hosts:
            ui.notify(
                f"Starting process",
                position="top-right",
            )

            for vm_id in vm_ids:
                print("Starting clone process")
                init_vmid = 700
                new_vm_ids.append(init_vmid)
                clone_host(
                    node=self.node_name, new_id=init_vmid, vmid_of_host_to_clone=vm_id
                )
                wait_for_unlock(
                    init_vmid, self.node_name
                )  # waits for host to get out of lock
                init_vmid += 1  # ← Don't forget to increment correctly

            ui.notify(
                f"Convert to template and add to pool",
                position="top-right",
            )

            #  convert those to templates
            #  Add to pool
            for new_vm_id in new_vm_ids:
                print(f"Converting {new_vm_id} to template and adding to pool")
                ui.notify(
                    f"Converting {new_vm_id} to template and adding to pool",
                    position="top-right",
                )
                print("converting")
                convert_to_template(vmid=new_vm_id, node=self.node_name)
                print("waiting")
                wait_for_unlock(new_vm_id, self.node_name)
                print("add_host_to_pool")
                add_host_to_pool(
                    poolid=template_pool_name,
                    vmid=new_vm_id,
                )
                print("hosted added to pool")

        except Exception as e:
            ui.notify(
                f"Error creating vapp template: {e}",
                position="top-right",
            )


class TemplatesView:
    def __init__(self):
        # Any initialization you need can go here
        pass

    def render(self):
        try:
            with ui.expansion("Templates", icon="work", caption="Templates...").classes(
                "w-full"
            ):
                ui.markdown("## Templates")
                for i in range(1, 3):
                    with ui.card().classes("w-full border"):
                        with ui.row().classes(
                            "w-full justify-between items-center mt-4 flex-1"
                        ):
                            ui.input("Pool Name").classes("flex-1")
                            ui.checkbox("Start Pool post clone").classes("flex-1")
                            ui.button("Clone").classes("flex-1")
            # ui.separator()

        except Exception as e:
            print(e)
            ui.notify(f"Error occurred: {e}", position="top-right", type="warning")

    def clone_vms(self):
        """
        Does a few things:

        1. Creates pool "PPM_<VAPP_NAME>
        2. Clones each VM template with the name PPM_TEMPLATE_<TEMPLATE_NAME>
        3. Add those new VM's to that pool
        4. Starts the VM's in that pool
        """


class ActivePoolsView:
    def __init__(self):
        # Any initialization you need can go here
        pass

    def render(self):
        try:
            with ui.expansion(
                "Active Pools", icon="work", caption="Active pools/Labs...", value=True
            ).classes("w-full"):
                proxmox_class = get_proxmox_class()
                ui.markdown("## Active Vapps")
                for pool in proxmox_class.pools.get():
                    pool_name = pool.get("poolid")
                    vm_ids_in_pool = get_all_vms_in_pool(pool_name=pool_name)
                    with ui.card().classes("w-full border"):
                        ui.markdown(f"### {pool_name}")
                        ui.label(pool.get("comment"))
                        with ui.row().classes(
                            "w-full justify-between items-center mt-4 flex-1"
                        ):
                            ui.button(
                                "Start",
                                on_click=partial(get_all_vms_in_pool, pool_name),
                            ).classes("w-full flex-1")
                            ui.button("Stop").classes("w-full flex-1")
                            ui.button("Restart").classes("w-full flex-1")
                            ui.button("Delete").classes("w-full flex-1")
                            select1 = ui.select(
                                ["snapshot1", "snapshot2", "snapshot3"],
                                value="snapshot1",
                            ).classes("border")
                            ui.button("< Revert to snapshot").classes("w-full flex-1")
                        ui.separator()
                        with ui.expansion("VM's in pool:").classes("w-full"):
                            for vmid in vm_ids_in_pool:
                                with ui.row().classes(
                                    "w-full justify-between items-center mt-4"
                                ):
                                    ui.label(get_vm_name(vmid))
                                    ui.button("Start", on_click=partial(start_vm, vmid))
                                    ui.button("Stop", on_click=partial(stop_vm, vmid))
                                    ui.button(
                                        "Restart", on_click=partial(restart_vm, vmid)
                                    )
                                    ui.separator()
            # ui.separator()

        except Exception as e:
            print(e)
            ui.notify(f"Error occurred: {e}", position="top-right", type="warning")
