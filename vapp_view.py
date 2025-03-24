from nicegui import app, ui


class VappPage:
    def __init__(self): ...

    def render(self):
        self.render_card()

    def render_card(self):
        # note, this is not final. maybe have some tempalte cards, then a list of
        # current vapps
        for i in range(1, 10):
            with ui.card().classes("w-full"):
                ui.button("Start")
                ui.button("Stop")
                ui.button("Clone")
