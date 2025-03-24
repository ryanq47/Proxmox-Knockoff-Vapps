from functools import wraps
from nicegui import app, ui
import requests
import re
import yarl
from dotenv import load_dotenv
import os

jwt_regex = r"^[A-Za-z0-9-_]+?\.[A-Za-z0-9-_]+\.([A-Za-z0-9-_]+)?$"


class AuthView:
    def __init__(self):
        self.username = None
        self.password = None
        # self.proxmox_url = proxmox_url  # url of server, full thing + protocol

    def render(self):
        # Clear user-specific session data on load of auth page
        # Doing this as a failsafe for dev, and if any session data gets left in there
        app.storage.user.clear()
        add_particles_background()
        ui.page_title("WhisperNet")

        with ui.column().classes(
            "items-center justify-center absolute-center w-full h-screen"
        ):
            with ui.card().classes("w-full max-w-sm p-6 shadow-lg"):
                ui.label("Login").classes(
                    "text-2xl font-bold text-center text-slate-600 mb-4"
                )
                ui.markdown(
                    "API address is set at run time, with the `--api-host` argument"
                )
                ui.separator().classes("mb-4")

                # Input fields and login button
                with ui.column().classes("gap-4 w-full"):
                    self.proxmox_url_input = (
                        ui.input("Server", placeholder="http(s)://<address>:<port>")
                        .props("outlined")
                        .classes("w-full")
                    )
                    # Config.set_api_host(host=self.proxmox_url.value)

                    self.username_input = (
                        ui.input("Username").props("outlined").classes("w-full")
                    )
                    self.password_input = (
                        ui.input("Password", password=True, password_toggle_button=True)
                        .props("outlined")
                        .classes("w-full")
                    ).on(
                        "keydown.enter",
                        lambda e: ui.notification(self.get_ticket()),
                    )

                    ui.button("Login", on_click=self.get_ticket).classes(
                        "bg-blue-500 text-white w-full hover:bg-blue-600 rounded-lg"
                    )

                # # Forgot password link centered below the form
                # ui.link("Forgot Password?", "/forgot-password").classes(
                #     "text-sm text-slate-500 mt-4 text-center"
                # )

    def get_ticket(self):
        # Retrieve the current values from the input fields ONLY on click of login
        try:
            proxmox_url = self.proxmox_url_input.value
            username = self.username_input.value
            password = self.password_input.value

            data = {"username": username, "password": password}
            print(proxmox_url)

            base_url = yarl.URL(proxmox_url)
            url = base_url / "api2" / "json" / "access" / "ticket"
            print(url)
            response = requests.post(url, data=data, verify=False)
            if response.status_code == 200:
                # print(response.json())
                ui.notify("Successful login", position="top-right")
                # set creds somewher, perhaps user storage?
                app.storage.user["auth_dict"] = response.json()

                ui.navigate.to("/")
                # return response
            else:
                ui.notify(
                    f"Could not login: {response.status_code}",
                    position="top-right",
                    type="negative",
                )
        except Exception as e:
            ui.notify(
                f"Could not login: {e}",
                position="top-right",
                type="negative",
            )


@ui.page("/logout")
def logout():
    check_login()
    app.storage.user.clear()  # Clear user-specific session data
    ui.notify("Logged out successfully", type="positive", position="top-right")
    ui.navigate.to("/auth")


def check_login():
    auth_dict = app.storage.user.get("auth_dict", {}).get("data", None)
    if auth_dict:
        return True
    else:
        ui.notify(
            "Please log in to access this page", type="negative", position="top-right"
        )
        ui.navigate.to("/auth")


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
