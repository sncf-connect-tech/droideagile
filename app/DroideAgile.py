from app.droide_ui import App, Screen, Button


class MainScreen(Screen):
    def __init__(self):
        Screen.__init__(self, background_image_name="background2.png")

        btn_random_picker = Button("Random Picker", (10, 350))
        self.add_ui_element(btn_random_picker)
        btn_random_picker = Button("Lego Mood", (10, 290))
        self.add_ui_element(btn_random_picker)
        btn_random_picker = Button("Meeting Timer", (10, 230))
        self.add_ui_element(btn_random_picker)


class DroideAgile(App):
    def __init__(self):
        App.__init__(self, MainScreen())
