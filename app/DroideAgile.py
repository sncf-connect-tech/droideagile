from app.droide_ui import App, Screen


class MainScreen(Screen):
    pass


class DroideAgile(App):

    def __init__(self):
        App.__init__(self, MainScreen())
