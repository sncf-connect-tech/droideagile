# from app.droid_brick_pi import BRICK_PI
import pygame

from app.droid_brick_pi import BRICK_PI
from app.droide_ui import App, Screen, Button, Panel, font_smaller, Label, QrCode, UiLabel
from app.lego_mood.Ui import LegoMoodScreen
from app.random_picker import RandomPickerScreen


class SetupScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self, background_image_name="background2.png")
        self.main_screen = main_screen
        self.txt = UiLabel("Droid Setup...", pygame.Rect(10, 200, 300, 50))

        self.add_ui_element(self.txt, (0, 0))

        self.ready_subscription = BRICK_PI.ready.subscribe(on_next=lambda info: self.txt.set_text(info),
                                                           on_error=lambda info: self.exit_app(info),
                                                           on_completed=lambda: self.app.set_current_screen(
                                                               self.main_screen))

    def on_activate(self):
        Screen.on_activate(self)
        BRICK_PI.start()

    def exit_app(self, info):
        self.log.error(info)
        self.app.quit_app()


class MainScreen(Screen):
    def __init__(self):
        Screen.__init__(self, background_image_name="background2.png")

        btn_random_picker = Button("Random Picker", on_click=lambda x: self.app.set_current_screen(RANDOM_PICKER))
        self.add_ui_element(btn_random_picker, (10, 350))
        btn_random_picker = Button("Lego Mood", on_click=self.lego_mood)
        self.add_ui_element(btn_random_picker, (10, 290))
        btn_random_picker = Button("Meeting Timer")
        self.add_ui_element(btn_random_picker, (10, 230))

        btn_shutdown = Button("Shutdown now...", size=(158, 30), idle_color=(255, 0, 0), hover_color=(250, 100, 100),
                              active_color=(255, 0, 255), text_font=font_smaller)
        self.add_ui_element(btn_shutdown, (162, 450))

        self.add_ui_element(Button("Exit now...", size=(158, 30), idle_color=(255, 0, 0), hover_color=(250, 100, 100),
                                   active_color=(255, 0, 255), text_font=font_smaller,
                                   on_click=lambda x: self.app.quit_app()), (0, 450))

        lbl_web = Label("http://127.0.0.1/remotecontrol")
        self.add_ui_element(lbl_web, (10, 57))

        qrcode_web = QrCode("http://127.0.0.1/remotecontrol")
        self.add_ui_element(qrcode_web, (9, 68))

        top_panel = Panel("Welcome Droid...")
        self.add_ui_element(top_panel, (0, 0))

    def lego_mood(self, owner):
        self.app.set_current_screen(LEGOMOOD_SCREEN)


MAIN_SCREEN = MainScreen()
SETUP_SCREEN = SetupScreen(MAIN_SCREEN)
LEGOMOOD_SCREEN = LegoMoodScreen(MAIN_SCREEN)
RANDOM_PICKER = RandomPickerScreen(MAIN_SCREEN)


class DroideAgile(App):
    def __init__(self):
        App.__init__(self)
        self.add_screen(SETUP_SCREEN)
        self.add_screen(LEGOMOOD_SCREEN)
        self.add_screen(RANDOM_PICKER)
        self.add_screen(MAIN_SCREEN)
        self.set_current_screen(SETUP_SCREEN)

    def clean_up(self):
        App.clean_up(self)
        BRICK_PI.stop()
