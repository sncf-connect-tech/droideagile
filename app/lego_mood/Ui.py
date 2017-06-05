from __future__ import print_function

import pygame

from app.droid_brick_pi import BRICK_PI
from app.droid_configuration import load_image
from app.droide_ui import Screen, Button, UiLabel

all_colors = ["black", "blue", "green", "yellow", "red", "white", "brown"]


def load_images(all_colors):
    return map(lambda color_name: load_image('brick_img/brick-' + color_name + '.png'), all_colors)


bricks = load_images(all_colors)


class MoodBrick:
    value_mapping = {
        1: ("red", 4),
        2: ("white", 5),
        3: ("yellow", 3),
        4: ("blue", 1),
        5: ("green", 2)
    }

    def __init__(self, value):
        self.value = value
        self.color = pygame.Color(MoodBrick.value_mapping[self.value][0])
        self.brick_pi_indice = MoodBrick.value_mapping[self.value][1]

        self.surface = pygame.Surface((75, 75))
        self.surface.fill(self.color)
        for i in range(0, 3):
            for j in range(0, 3):
                self.surface.blit(bricks[self.brick_pi_indice], (i * 25, j * 25))
        self.active = False

    def render_at(self, display, offset_y=0):
        if self.active:
            outline = self.surface.get_rect().inflate(6, 6).move(10, offset_y)
            pygame.draw.rect(display, pygame.Color("orange"), outline, 3)
        display.blit(self.surface, (10, offset_y))


class MoodState:
    def __init__(self, screen):
        self.screen = screen

    def exit_state(self):
        pass

    def render(self, display):
        pass


class Reading(MoodState):
    def __init__(self, screen):
        MoodState.__init__(self, screen)
        self.txt = UiLabel("Reading...", pygame.Rect(100, 10, 200, 30))
        self.current_mood = None
        self.color_pickers = []
        for i in range(1, 6):
            self.color_pickers.append(MoodBrick(i))

        def select_mood_brick(c):
            if self.current_mood is not None:
                self.current_mood.active = False
            if 0 < c < 5:
                # check if we have a new color
                if self.screen.boot_color != c:
                    self.current_mood = filter(lambda x: x.brick_pi_indice == c, self.color_pickers)[0]
                    self.current_mood.active = True

        self.color_observer = BRICK_PI.buffered_color_sensor_observable.subscribe(
            on_next=lambda c: select_mood_brick(c))

    def render(self, display):
        i = 10
        for color_picker in self.color_pickers:
            color_picker.render_at(display, i)
            i += color_picker.surface.get_rect().height + 10
        self.txt.render(display)

    def exit_state(self):
        self.color_observer.dispose()


class Calibrating(MoodState):
    def __init__(self, screen):
        MoodState.__init__(self, screen)
        self.txt = UiLabel("Calibrating...", pygame.Rect(10, 200, 300, 50))

        def set_boot_color(c):
            self.screen.log.debug("boot color is " + str(c))
            self.screen.boot_color = c
            self.screen.change_state(Reading(self.screen))

        self.color_observer = BRICK_PI.buffered_color_sensor_observable.subscribe(
            on_next=lambda c: set_boot_color(c))

    def exit_state(self):
        self.color_observer.dispose()

    def render(self, display):
        self.txt.render(display)


class LegoMoodScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self, background_image_name="brick_img/brick-background.png")

        self.boot_color = None
        self.main_screen = main_screen

        btn_back = Button("Back", on_click=self.back, size=(100, 30))
        self.add_ui_element(btn_back, (10, 440))

        # self.state_label = ReplaySubject()
        # self.state_label.on_next("Calibrating...")
        # self.add_ui_element(Label2(self.state_label, text_color=(255, 0, 0)), (0, 300))

        # self.color_observer = None

        self.state = None

    def change_state(self, new_state):
        if self.state is not None:
            self.state.exit_state()
        self.state = new_state

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
        self.state = Calibrating(self)

    def on_deactivate(self):
        pass

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

    def render(self, display):
        Screen.render(self, display)
        # if self.current_color > -1:
        #     display.blit(bricks[self.current_color], (50, 50))
        if self.state is not None:
            self.state.render(display)
