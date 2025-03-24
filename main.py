from nicegui import events, ui, app
from auth import AuthView, check_login
import logging
from vapp_view import VappPage

logging.getLogger("niceGUI").setLevel(logging.CRITICAL)


@ui.page("/")
def index():
    check_login()
    v = VappPage()
    v.render()


@ui.page("/auth")
def auth_view_page():
    # navbar()
    a = AuthView()
    a.render()


# Note - this dir has no auth
app.add_static_files(
    "/static", "static"
)  # Serve files from the 'static' directory, to /static
ui.run(storage_secret="URMOM", host="0.0.0.0")
