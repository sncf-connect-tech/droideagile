import random

import pygame
from rx import Observable

from app.droid_brick_pi import BRICK_PI
from app.droide_ui import Screen, Button, UiLabel
from app.wall_e import WallE


class RandomPickerScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self)
        self.main_screen = main_screen
        self.add_ui_element(Button("Back", on_click=self.back, size=(140, 30)), (10, 440))
        self.wall_e = WallE()
        self.wall_e.rect.x = 10
        self.wall_e.rect.y = 10
        self.add_sprite(self.wall_e)

        self.state = "picking"

        self.wheel_power = 255
        self.head_power = 255
        self.one_lap_seconds = 10
        self.max_rotate_seconds = 15
        self.change_head_every_seconds = 5
        self.direction = 1

        self.txt = UiLabel("", pygame.Rect(10, 10, 300, 50))
        self.add_ui_element(self.txt, (0, 0))

    def update_sprite(self):
        Screen.update_sprite(self)
        if self.state == "picking":
            self.wall_e.move(self.direction)
        else:
            self.wall_e.dirty = 0
            self.wall_e.visible = 0

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

    def on_activate(self):
        Screen.on_activate(self)
        self.rotate_motors()

    def rotate_motors(self):
        BRICK_PI.set_left_speed(self.wheel_power * self.direction)
        BRICK_PI.set_right_speed(-self.wheel_power * self.direction)
        BRICK_PI.set_head_speed(self.head_power)

        maxTime = int(round(random.uniform(self.one_lap_seconds, self.max_rotate_seconds)*1000))
        self.log.debug("rotating {}s".format(maxTime))
        self.txt.set_text("rotating {}s".format(maxTime))

        # BrickPi.MotorSpeed[left_wheel_port] = wheel_power * direction  # Set the speed of MotorA (-255 to 255)
        # BrickPi.MotorSpeed[right_wheel_port] = -wheel_power * direction  # Set the speed of MotorD (-255 to 255)

        def stop_sequence(direction_observer):
            self.log.debug("stop sequence")
            self.state = "done"
            self.txt.set_text("done !")
            direction_observer.dispose()

        def change_direction_of_head():
            BRICK_PI.set_head_speed(self.head_power * (-1))

        direction_observer = Observable.interval(5000).subscribe(on_next=lambda x: change_direction_of_head())
        Observable.timer(maxTime).subscribe(on_completed=lambda: stop_sequence(direction_observer))
