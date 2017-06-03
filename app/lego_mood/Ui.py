from __future__ import print_function
import pygame

from app.droid_brick_pi import BRICK_PI
from app.droide_ui import Screen, Button, Panel


class LegoMoodScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self, background_image_name="brick_img/brick-background.png")

        self.main_screen = main_screen

        btn_back = Button("Back", on_click=self.back)
        self.add_ui_element(btn_back, (10, 400))

        btn_read_current_color = Button("Read Current Color", on_click=self.read_current_color)
        self.add_ui_element(btn_read_current_color, (10, 100))

        top_panel = Panel("Lego Mood")
        self.add_ui_element(top_panel, (0, 0))

        self.state = "Calibrating..."
        self.state_panel = Panel(self.state)
        self.add_ui_element(self.state_panel, (0, 300))

        self.color_observer = None

    def set_up(self):
        Screen.set_up(self)
        # get app surface size
        rect = self.app.get_surface_rect()
        # create full_background
        full_background = pygame.Surface((rect.w, rect.h))
        # fill it
        for i in range(0, 13):
            for j in range(0, 20):
                full_background.blit(self.background, (i * 25, j * 25))
        # overwrite self background with new background
        self.background = full_background

    def on_activate(self):
        self.color_observer = BRICK_PI.droid_sensors.subscribe(on_next=lambda c: print(str(c.color)))

    def on_deactivate(self):
        self.color_observer.dispose()

    def read_current_color(self, owner):
        color = BRICK_PI.color_sensor_queue.get_nowait()
        self.log.info("current color is: " + str(color))

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

