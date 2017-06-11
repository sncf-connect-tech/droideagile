import random

import pygame
from rx import Observable

from app.droid_brick_pi import BRICK_PI
from app.droid_configuration import path_to_image
from app.droide_ui import Screen, Button, UiLabel
from app.third_party.pyignition import PyIgnition
from app.wall_e import WallE


class RandomPickerScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self)
        self.main_screen = main_screen
        self.add_ui_element(Button("Back", on_click=self.back, size=(140, 30)), (10, 440))
        self.wall_e = WallE()
        self.add_sprite(self.wall_e)

        self.state = "picking"
        self.wheel_power = 255
        self.head_power = 255
        self.one_lap_seconds = 5
        self.max_rotate_seconds = 10
        self.change_head_every_seconds = 2
        self.direction = 1

        self.txt = UiLabel("", pygame.Rect(10, 10, 300, 50))
        self.add_ui_element(self.txt, (0, 0))

    def set_up(self):
        Screen.set_up(self)
        self.wheel = PyIgnition.ParticleEffect(self.app.surface, (0, 0), (300, 300))
        self.flame = self.wheel.CreateSource((150, 150), initspeed=20.0, initdirection=0.0, initspeedrandrange=0.0,
                                             initdirectionrandrange=0.5, particlesperframe=3, particlelife=50,
                                             drawtype=PyIgnition.DRAWTYPE_SCALELINE, colour=(255, 200, 200),
                                             length=20.0)
        self.sparks = self.wheel.CreateSource((150, 150), initspeed=1.0, initdirection=0.0, initspeedrandrange=0.9,
                                              initdirectionrandrange=3.141592653, particlesperframe=1, particlelife=300,
                                              genspacing=3, drawtype=PyIgnition.DRAWTYPE_IMAGE,
                                              imagepath=path_to_image("Spark.png"))
        self.wheel.CreateDirectedGravity(strength=0.05, direction=[0, 1])

    def render(self, display):
        Screen.render(self, display)
        if self.state != "picking":
            self.flame.SetInitDirection(self.flame.initdirection + self.velocity)
            if self.flame.curframe % 30 == 0:
                self.flame.ConsolidateKeyframes()

            if self.velocity <= self.maxvelocity:
                self.velocity += self.acceleration
            self.wheel.Update()
            self.wheel.Redraw()

    def render_background(self, display):
        if self.state != "picking":
            display.fill((100, 100, 100))

    def update_sprite(self):
        Screen.update_sprite(self)
        if self.state == "picking":
            self.wall_e.move(self.direction)
        else:
            self.wall_e.dirty = 1
            self.wall_e.visible = 0

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

    def on_activate(self):
        Screen.on_activate(self)
        self.velocity = 0.1
        self.maxvelocity = 0.5
        self.acceleration = 0.001

        self.wall_e.dirty = 1
        self.wall_e.visible = 1
        self.wall_e.rect.x = 10
        self.wall_e.rect.y = 200
        self.state = "picking"

        self.rotate_motors()

    def rotate_motors(self):
        BRICK_PI.set_left_speed(self.wheel_power * self.direction)
        BRICK_PI.set_right_speed(-self.wheel_power * self.direction)
        BRICK_PI.set_head_speed(self.head_power)

        maxTime = int(round(random.uniform(self.one_lap_seconds, self.max_rotate_seconds)))
        self.log.debug("rotating {}s".format(maxTime))
        self.txt.set_text("rotating {}s".format(maxTime))

        # BrickPi.MotorSpeed[left_wheel_port] = wheel_power * direction  # Set the speed of MotorA (-255 to 255)
        # BrickPi.MotorSpeed[right_wheel_port] = -wheel_power * direction  # Set the speed of MotorD (-255 to 255)

        def stop_sequence(direction_observer):
            self.log.debug("stop sequence")
            self.state = "done"
            self.txt.set_text("done !")
            BRICK_PI.set_left_speed(0)
            BRICK_PI.set_right_speed(0)
            BRICK_PI.set_head_speed(0)
            direction_observer.dispose()
            tic_tac_observer.dispose()

        def change_direction_of_head():
            BRICK_PI.set_head_speed(self.head_power * (-1))

        direction_observer = Observable.interval(self.change_head_every_seconds).subscribe(
            on_next=lambda x: change_direction_of_head())
        tic_tac_observer = Observable.interval(1000).subscribe(
            on_next=lambda x: self.txt.set_text("rotating {}s".format(maxTime - x - 1)))
        Observable.timer(maxTime * 1000).subscribe(on_completed=lambda: stop_sequence(direction_observer))
