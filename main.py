from nicegui import events, ui, app
import logging
from vapp_view import VappPage
from auth import *
from database import clear_credentials

logging.getLogger("niceGUI").setLevel(logging.CRITICAL)


@ui.page("/")
def main_page() -> None:
    def logout() -> None:
        app.storage.user.clear()
        clear_credentials()  # Nukes the SQLite-stored credentials
        ui.navigate.to("/login")

    v = VappPage()
    v.render()


if __name__ in {"__main__", "__mp_main__"}:
    # Note - this dir has no auth
    app.add_static_files(
        "/static", "static"
    )  # Serve files from the 'static' directory, to /static
    ui.run(storage_secret="URMOM", host="0.0.0.0", show=False)
