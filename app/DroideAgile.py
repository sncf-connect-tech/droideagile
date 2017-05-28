from app.droide_ui import App, Screen, Button, Panel, font_smaller, Label, QrCode


class MainScreen(Screen):
    def __init__(self):
        Screen.__init__(self, background_image_name="background2.png")

        btn_random_picker = Button("Random Picker")
        self.add_ui_element(btn_random_picker, (10, 350))
        btn_random_picker = Button("Lego Mood")
        self.add_ui_element(btn_random_picker, (10, 290))
        btn_random_picker = Button("Meeting Timer")
        self.add_ui_element(btn_random_picker, (10, 230))

        btn_shutdown = Button("Shutdown now...", size=(320, 30), idle_color=(255, 0, 0), hover_color=(250, 100, 100),
                              active_color=(255, 0, 255), text_font=font_smaller)
        self.add_ui_element(btn_shutdown, (0, 450))

        lbl_web = Label("http://127.0.0.1/remotecontrol")
        self.add_ui_element(lbl_web, (10, 57))

        qrcode_web = QrCode("http://127.0.0.1/remotecontrol")
        self.add_ui_element(qrcode_web, (9, 68))

        top_panel = Panel("Welcome Droid...")
        self.add_ui_element(top_panel, (0, 0))


class DroideAgile(App):
    def __init__(self):
        App.__init__(self, MainScreen())
