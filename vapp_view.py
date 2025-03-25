from nicegui import app, ui
import requests
import yarl
from utils import get_proxmox_class


class VappPage:
    def __init__(self): ...

    def render(self):
        with ui.row().classes("w-full justify-between items-center mt-4"):
            ui.markdown("# Proxmox Pools Manager")
            ui.button("Logout", on_click=lambda: ui.navigate.to("/logout"))
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
                with ui.card().classes("w-full border") as card:
                    ui.markdown(f'### {pool.get("poolid")}')
                    ui.label(pool.get("comment"))

                    # Flex container for buttons spread out evenly
                    with ui.row().classes(
                        "w-full justify-between items-center mt-4 flex-1"
                    ):
                        ui.button("Start").classes("w-full flex-1")
                        ui.button("Stop").classes("w-full flex-1")
                        ui.button("Restart").classes("w-full flex-1")
                        ui.button("Delete").classes("w-full flex-1")
                        select1 = ui.select(
                            ["snapshot1", "snapshot2", "snapshot3"], value="snapshot1"
                        ).classes("border")
                        ui.button("< Revert to snapshot").classes("w-full flex-1")

                        ui.separator()

                        with ui.expansion("VM's in pool:").classes("w-full"):
                            for i in range(1, 3):
                                with ui.row().classes(
                                    "w-full justify-between items-center mt-4 "
                                ):
                                    ui.label(f"VM_{i}")
                                    ui.button("Start")
                                    ui.button("stop")
                                    ui.separator()
        except Exception as e:
            print(e)
            ui.notify(f"Error occured: {e}", position="top-right", type="warning")
