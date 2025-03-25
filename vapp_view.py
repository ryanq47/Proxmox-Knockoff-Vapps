from nicegui import app, ui
import requests
import yarl
from utils import get_proxmox_class


class VappPage:
    def __init__(self): ...

    def render(self):
        self.render_card()

    def render_card(self):
        try:
            # note, this is not final. maybe have some tempalte cards, then a list of
            # current vapps
            for i in range(1, 3):
                with ui.card().classes("w-full"):
                    ui.button("Start")
                    ui.button("Stop")
                    ui.button("Clone")

            proxmox_class = get_proxmox_class()

            for node in proxmox_class.nodes.get():
                print(node)
                for vm in proxmox_class.nodes(node["node"]).qemu.get():
                    ui.label(f"{vm['vmid']}. {vm['name']} => {vm['status']}")

        except Exception as e:
            print(e)
            ui.notify(f"Error occured: {e}", position="top-right", type="warning")
