from __future__ import print_function

import pygame
from rx.subjects import ReplaySubject

from app.droid_brick_pi import BRICK_PI
from app.droid_configuration import load_image
from app.droide_ui import Screen, Button, Panel, Label2

all_colors = ["black", "blue", "green", "yellow", "red", "white", "brown"]


def load_images(all_colors):
    return map(lambda color_name: load_image('brick_img/brick-' + color_name + '.png'), all_colors)


bricks = load_images(all_colors)


class LegoMoodScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self, background_image_name="brick_img/brick-background.png")

        self.current_color = -1
        self.main_screen = main_screen

        btn_back = Button("Back", on_click=self.back)
        self.add_ui_element(btn_back, (10, 400))

        btn_read_current_color = Button("Read Current Color", on_click=self.read_current_color)
        self.add_ui_element(btn_read_current_color, (10, 100))

        top_panel = Panel("Lego Mood")
        self.add_ui_element(top_panel, (0, 0))

        self.state_label = ReplaySubject()
        self.state_label.on_next("Calibrating...")
        self.add_ui_element(Label2(self.state_label, text_color=(255, 0, 0)), (0, 300))

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

        self.color_observer = BRICK_PI.buffered_color_sensor_observable.subscribe(
            on_next=lambda c: set_current_color(c))

        def set_current_color(x):
            self.state_label.on_next("Color is " + str(x))
            self.current_color = x

    def on_deactivate(self):
        self.color_observer.dispose()

    def read_current_color(self, owner):
        self.log.info("current color is: " + str(self.current_color))

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

    def render(self, display):
        Screen.render(self, display)
        if self.current_color > -1:
            display.blit(bricks[self.current_color], (50, 50))
