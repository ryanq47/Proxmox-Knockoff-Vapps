from functools import wraps
from nicegui import app, ui
from proxmoxer import ProxmoxAPI
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from database import set_credential

unrestricted_page_routes = {"/login"}


class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get("authenticated", False):
            if (
                not request.url.path.startswith("/_nicegui")
                and request.url.path not in unrestricted_page_routes
            ):
                return RedirectResponse(f"/login?redirect_to={request.url.path}")
        return await call_next(request)


# add middleware

app.add_middleware(AuthMiddleware)


@ui.page("/login")
def login(redirect_to: str = "/") -> Optional[RedirectResponse]:
    def try_login() -> None:
        proxmox = ProxmoxAPI(
            proxmox_url_input.value,
            user=username_input.value,
            password=password_input.value,
            verify_ssl=False,
        )

        # Store credentials (or just the URL and username, token, etc.)
        set_credential("proxmox_url", proxmox_url_input.value)
        set_credential("username", username_input.value)
        set_credential("password", password_input.value)

        # Optionally, store a token if available:
        # set_credential("token", token_value)

        if proxmox:
            app.storage.user.update({"authenticated": True})
            ui.navigate.to(redirect_to)
        else:
            ui.notify("Wrong username or password", color="negative")

    if app.storage.user.get("authenticated", False):
        return RedirectResponse("/")

    with ui.card().classes("absolute-center"):
        proxmox_url_input = (
            ui.input("Server", placeholder="<address>:<port>")
            .props("outlined")
            .classes("w-full")
        )
        username_input = ui.input("Username").props("outlined").classes("w-full")
        password_input = (
            ui.input("Password", password=True, password_toggle_button=True)
            .props("outlined")
            .classes("w-full")
        )
        ui.button("Log in", on_click=try_login)


# @ui.page("/particles")
# bug cuz not being displayed in login page. prolly something with css in the login func
def add_particles_background():
    # Add the particles.js container and load the existing configuration
    ui.add_body_html(
        """
    <div id="particles-js" style="position: fixed; width: 100%; height: 100%; z-index: -1;"></div>
    <script src="/static/particles.js"></script>
    <script>
        // Load particles.js with your existing configuration
        particlesJS.load('particles-js', '/static/particlesjs-config.json', function() {
            console.log('particles.js loaded - callback');
        });
    </script>
    """
    )
