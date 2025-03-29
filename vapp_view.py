from nicegui import app, ui
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
                value=node_list[0],  # default first node
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
            TemplatesView(node_name=self.currently_selected_node.value).render()

        # Active Pools section using the ActivePoolsView class

        self.active_pools_container = ui.column().classes("w-full")
        with self.active_pools_container:
            ActivePoolsView(self.currently_selected_node.value).render()

    def on_node_changed(self):
        # Update node-dependent sections without duplicating the expansion blocks.
        self.vapp_creator_container.clear()
        vcw = VappCreatorView(node_name=self.currently_selected_node.value)
        vcw.render()

        self.templates_container.clear()
        TemplatesView(node_name=self.currently_selected_node.value).render()

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
            # print(raw_vm_data)
            with ui.step("[Optional] Select VM's to include in template"):
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
                ui.button(
                    "Create Template from Selected VM's", on_click=self._create_template
                ).classes("w-full flex-1")
                ui.label(
                    "Note... please just click this once. There's a UI bug that prevents any notifications from coming on screen here. On success, a new Template will show up in the Template section"
                )
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
                # print(row)
                # toss all id's in their own list
                vm_ids.append(row.get("vmid"))
                # ui.notify(
                #     f'Adding cloned {row.get("name")} to vapp {self.vapp_name.value}',
                #     position="top-right",
                # )

            # create a NIC, ex: "POOLNAME-NIC"
            # https://pve.proxmox.com/pve-docs/api-viewer/index.html#/nodes/{node}/network

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
                # print("Starting clone process")
                init_vmid = get_next_available_vmid()
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
                # print(f"Converting {new_vm_id} to template and adding to pool")
                ui.notify(
                    f"Converting {new_vm_id} to template and adding to pool",
                    position="top-right",
                )
                # print("converting")
                convert_to_template(vmid=new_vm_id, node=self.node_name)
                # print("waiting")
                wait_for_unlock(new_vm_id, self.node_name)
                # print("add_host_to_pool")
                add_host_to_pool(
                    poolid=template_pool_name,
                    vmid=new_vm_id,
                )
                # print("hosted added to pool")

        except Exception as e:
            ui.notify(
                f"Error creating vapp template: {e}",
                position="top-right",
            )


class TemplatesView:
    def __init__(self, node_name):
        # Any initialization you need can go here
        self.node_name = node_name

    def render(self):
        try:
            with ui.expansion("Templates", icon="work", caption="Templates...").classes(
                "w-full"
            ):
                ui.markdown("## Templates")
                # for i in range(1, 3):

                valid_template_pool_list = get_valid_templates()

                for template_pool_name in valid_template_pool_list:
                    print(template_pool_name)
                    with ui.card().classes("w-full border"):
                        ui.label(template_pool_name)
                        with ui.row().classes(
                            "w-full justify-between items-center mt-4 flex-1"
                        ):
                            vapp_name_input = ui.input(
                                "New VAPP Name (7 characters MAX due to proxmox limitations)"
                            ).classes("flex-1")
                            self.start_vms_post_clone = ui.checkbox(
                                "Start Pool post clone", value=True
                            ).classes("flex-1")
                            ui.button(
                                "Clone",
                                on_click=lambda tpn=template_pool_name, inp=vapp_name_input: self.create_vapp_from_template(
                                    tpn, inp.value
                                ),
                            ).classes("flex-1")
            # ui.separator()

        except Exception as e:
            # print(e)
            ui.notify(f"Error occurred: {e}", position="top-right", type="warning")

    def create_vapp_from_template(self, template_pool_name, new_pool_name):
        """
        Does a few things:

        1. Creates pool "PPM_<VAPP_NAME>"
        2. Clones each VM template with the name PPM_TEMPLATE_<TEMPLATE_NAME>
        3. Add those new VM's to that pool
        4. Starts the VM's in that pool
        """

        new_pool_name = f"PPM_{new_pool_name}"

        logger.info(
            f"Creating VAPP from template pool '{template_pool_name}' into new pool '{new_pool_name}'"
        )

        # 1. Get all VM's in template pool
        vms_in_template_pool = get_all_vms_in_pool(template_pool_name)
        logger.info(
            f"Found {len(vms_in_template_pool)} VM(s) in template pool '{template_pool_name}'"
        )

        # 2. Create new pool with new pool name
        create_pool(poolid=new_pool_name)
        logger.info(f"Created new pool '{new_pool_name}'")

        # creat nic EXPLICITLY on new vapp creation, NOT at template time like it used to be
        create_nic(
            iface_name=f"{new_pool_name}_NIC",
            node=self.node_name,  # user input for which node to clone to
            type="bridge",
        )

        list_of_new_vm_ids = []
        # .2. Clone all VM's - thinclone
        for vm_id in vms_in_template_pool:
            new_vmid = get_next_available_vmid()
            list_of_new_vm_ids.append(new_vmid)
            logger.info(f"Cloning VM {vm_id} into new VM {new_vmid}")
            clone_host(
                new_id=new_vmid, vmid_of_host_to_clone=vm_id, node=self.node_name
            )

            logger.info(f"Waiting for VM {new_vmid} to unlock")
            wait_for_unlock(vmid=new_vmid, node=self.node_name)

            logger.info(f"Adding cloned VM {new_vmid} to pool '{template_pool_name}'")
            add_host_to_pool(
                poolid=new_pool_name,
                vmid=new_vmid,
            )

            add_existing_bridge_to_vm(
                vmid=new_vmid,
                node=self.node_name,
                bridge_name=f"{new_pool_name}_NIC",
            )

            # if self.start_vms_post_clone:
            #     start_vm(node=self.node_name, vmid=new_vmid)

            new_vmid += 1

        if self.start_vms_post_clone:

            start_multiple_vms(vmid_list=list_of_new_vm_ids, node=self.node_name)


class ActivePoolsView:
    def __init__(self, node_name):
        self.node_name = node_name

    def render(self):
        try:
            with ui.expansion(
                "Active Pools", icon="work", caption="Active pools/Labs...", value=True
            ).classes("w-full"):
                proxmox_class = get_proxmox_class()
                ui.markdown("## Active Vapps")

                for pool in get_vapps():  # for each pool/VAPP... do this
                    self.render_pool(pool)

        except Exception as e:
            # print(e)
            ui.notify(f"Error occurred: {e}", position="top-right", type="warning")

    def render_pool(self, pool):
        pool_name = pool.get("poolid")
        vm_ids_in_pool = get_all_vms_in_pool(pool_name=pool_name)

        with ui.card().classes("w-full border"):
            display_pool_name = pool_name.replace("_", "\\_")
            ui.markdown(f"### {display_pool_name}")  # add in delim for _
            ui.label(pool.get("comment"))
            # ui.label("WAN ip: someip")
            self.render_pool_controls(pool_name, vm_ids_in_pool)
            self.render_pool_vms(vm_ids_in_pool)

    def render_pool_controls(self, pool_name, vm_ids_in_pool):
        with ui.row().classes("w-full justify-between items-center mt-4 flex-1"):
            ui.button(
                "Start",
                on_click=partial(
                    start_multiple_vms,
                    vmid_list=vm_ids_in_pool,
                    node=self.node_name,
                ),
            ).classes("w-full flex-1")

            ui.button(
                "Stop",
                on_click=partial(
                    stop_multiple_vms,
                    vmid_list=vm_ids_in_pool,
                    node=self.node_name,
                ),
            ).classes("w-full flex-1")

            ui.button(
                "Restart",
                on_click=partial(
                    restart_multiple_vms,
                    vmid_list=vm_ids_in_pool,
                    node=self.node_name,
                ),
            ).classes("w-full flex-1")

            ui.button(
                "Delete VAPP",
                on_click=partial(
                    delete_vapp,
                    vmid_list=vm_ids_in_pool,
                    node=self.node_name,
                    pool_name=pool_name,
                ),
            ).classes("w-full flex-1")

            # I don't wanna deal with this rn so no snapshots atm
            # select1 = ui.select(
            #     ["snapshot1", "snapshot2", "snapshot3"],
            #     value="snapshot1",
            # ).classes("border")
            # ui.button("< Revert to snapshot").classes("w-full flex-1")

        ui.separator()

    def render_pool_vms(self, vm_ids_in_pool):
        with ui.expansion("VM's in pool:").classes("w-full"):
            for vmid in vm_ids_in_pool:
                self.render_single_vm(vmid)

    def render_single_vm(self, vmid):
        with ui.row().classes("w-full justify-between items-center mt-4"):
            ui.label(get_vm_name(vmid))
            ui.label(f"Status: {get_vm_status(vmid, self.node_name)}")
            ui.button("Start", on_click=partial(start_vm, vmid, self.node_name))
            ui.button("Stop", on_click=partial(stop_vm, vmid, self.node_name))
            ui.button(
                "Revert to snapshot",
                on_click=partial(self.render_revert_snapshots_dialogue, vmid),
            )
            ui.button(
                "Take Snapshot",
                on_click=partial(self.render_take_snapshots_dialogue, vmid),
            )
            ui.button("Restart", on_click=partial(restart_vm, vmid, self.node_name))
            ui.separator()

    async def render_revert_snapshots_dialogue(self, vmid):
        """
        qdialog for snapshots
        """
        with ui.dialog() as dialog, ui.card():
            snapshot_options = list_snapshots(node=self.node_name, vmid=vmid)

            with ui.element().classes("w-full"):
                snapshot_name_input = ui.select(
                    options=snapshot_options,
                    label="VM Snapshots",
                )

            with ui.row():
                ui.button(
                    "Revert to Snapshot",
                    on_click=lambda: dialog.submit(
                        {"snapshot_name": snapshot_name_input.value}
                    ),
                )
                ui.button("Cancel", on_click=lambda: dialog.submit(None))

        dialog.open()
        result = await dialog

        if result is not None:
            try:
                revert_snapshot(
                    snapshot_name=result.get("snapshot_name", ""),
                    vmid=vmid,
                    node=self.node_name,
                )
                ui.notify(
                    f"VM {vmid} reverted to snapshot '{result.get('snapshot_name')}'",
                    position="top-right",
                )
            except Exception as e:
                logger.error(f"Error reverting VM {vmid} to snapshot: {e}")
                ui.notify(
                    f"Error reverting snapshot: {e}",
                    type="warning",
                    position="top-right",
                )
        else:
            ui.notify("Snapshot reverter was cancelled", position="top-right")

    async def render_take_snapshots_dialogue(self, vmid):
        """
        qdialog for snapshots
        """
        with ui.dialog() as dialog, ui.card():
            with ui.element().classes("w-full"):
                snapshot_name_input = ui.input("Snapshot Name:")
                snapshot_desc_input = ui.input("Snapshot Desc:")

            with ui.row():
                ui.button(
                    "Take Snapshot",
                    on_click=lambda: dialog.submit(
                        {
                            "snapshot_name": snapshot_name_input.value,
                            "snapshot_desc_input": snapshot_desc_input.value,
                        }
                    ),
                )
                ui.button("Cancel", on_click=lambda: dialog.submit(None))

        dialog.open()
        result = await dialog

        if result is not None:
            try:
                take_snapshot(
                    vmid=vmid,
                    node=self.node_name,
                    snapshot_name=result["snapshot_name"],
                    description=result["snapshot_desc_input"] or "",
                )
                ui.notify(
                    f"Snapshot '{result['snapshot_name']}' taken for VM {vmid}",
                    position="top-right",
                )
            except Exception as e:
                logger.error(f"Error taking snapshot for VM {vmid}: {e}")
                ui.notify(
                    f"Error taking snapshot: {e}", type="warning", position="top-right"
                )
        else:
            ui.notify("Snapshot creation was cancelled", position="top-right")


# list_snapshots
