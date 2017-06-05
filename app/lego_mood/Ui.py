from __future__ import print_function

import pygame
from pygame.constants import BLEND_RGBA_MULT
from rx import Observable

from app.droid_brick_pi import BRICK_PI
from app.droid_configuration import load_image
from app.droide_ui import Screen, Button, UiLabel, Element

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

    def __init__(self, value, size=(75,75)):
        self.value = value
        self.color_name = MoodBrick.value_mapping[self.value][0]
        self.color = pygame.Color(self.color_name)
        self.brick_pi_indice = MoodBrick.value_mapping[self.value][1]

        self.size = size
        self.surface = pygame.Surface(size)
        self.surface.fill(self.color)
        for i in range(0, self.size[0] / 25):
            for j in range(0, self.size[1] / 25):
                self.surface.blit(bricks[self.brick_pi_indice], (i * 25, j * 25))
        self.active = False

    def render_at(self, display, offset_x=10, offset_y=0):
        if self.active:
            outline = self.surface.get_rect().inflate(6, 6).move(offset_x, offset_y)
            pygame.draw.rect(display, pygame.Color("orange"), outline, 3)
        display.blit(self.surface, (offset_x, offset_y))


class MoodState:
    def __init__(self, screen):
        self.screen = screen

    def exit_state(self):
        pass

    def render(self, display):
        pass


class StateWithAllMoods(MoodState):
    def __init__(self, screen, color_pickers=None):
        MoodState.__init__(self, screen)
        if color_pickers is None:
            self.color_pickers = []
            for i in range(1, 6):
                self.color_pickers.append(MoodBrick(i))
        else:
            self.color_pickers = color_pickers

    def render(self, display):
        i = 10
        for color_picker in self.color_pickers:
            color_picker.render_at(display, 10, i)
            i += color_picker.surface.get_rect().height + 10


class Displaying(StateWithAllMoods):
    def __init__(self, screen, selected_mood_brick):
        StateWithAllMoods.__init__(self, screen, color_pickers=[selected_mood_brick])
        self.txt = UiLabel("Read color " + str(selected_mood_brick.color_name), pygame.Rect(100, 10, 200, 30))

        self.screen.totem.add_mood_brick(selected_mood_brick)

        self.waiting = Observable.timer(2000).subscribe(on_completed=self.get_back_to_reading)

    def get_back_to_reading(self):
        if self.screen.totem.is_full():
            self.screen.done_with_reading(None)
        else:
            self.screen.change_state(Reading(self.screen))

    def render(self, display):
        StateWithAllMoods.render(self, display)
        self.txt.render(display)

    def exit_state(self):
        self.waiting.dispose()


class Reading(StateWithAllMoods):
    def __init__(self, screen):
        StateWithAllMoods.__init__(self, screen)
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
                    if not self.screen.closing:
                        self.screen.change_state(Displaying(self.screen, self.current_mood))

        self.color_observer = BRICK_PI.buffered_color_sensor_observable.subscribe(
            on_next=lambda c: select_mood_brick(c))

    def render(self, display):
        StateWithAllMoods.render(self, display)
        self.txt.render(display)

    def exit_state(self):
        self.color_observer.dispose()


class Calibrating(MoodState):
    def __init__(self, screen):
        MoodState.__init__(self, screen)
        self.screen.totem.visible = False
        self.txt = UiLabel("Calibrating...", pygame.Rect(10, 200, 300, 50))

        def set_boot_color(c):
            self.screen.log.debug("boot color is " + str(c))
            self.screen.boot_color = c
            self.screen.change_state(Reading(self.screen))

        self.color_observer = BRICK_PI.buffered_color_sensor_observable.subscribe(
            on_next=lambda c: set_boot_color(c))

    def exit_state(self):
        self.screen.totem.visible = True
        self.color_observer.dispose()

    def render(self, display):
        self.txt.render(display)


class MoodTotem(Element):
    def __init__(self):
        Element.__init__(self)
        self.surface = pygame.Surface((200, 340))
        self.surface.fill(pygame.Color("lightgray"))
        self.mood_bricks = []

    def render(self, display):
        Element.render(self, display)
        display.blit(self.surface, self.position, None, BLEND_RGBA_MULT)
        x = 2
        y = 2
        for b in self.mood_bricks:
            if y + b.surface.get_rect().height + 2 > self.surface.get_rect().height:
                y = 2
                x += b.surface.get_rect().width + 2
            b.render_at(display, self.position[0]+x, self.position[1] + y)
            y += b.surface.get_rect().height + 2

    def add_mood_brick(self, mood_brick):
        self.mood_bricks.append(MoodBrick(mood_brick.value, size=(50,50)))

    def is_full(self):
        return len(self.mood_bricks) >= 16


class LegoMoodScreen(Screen):
    def __init__(self, main_screen):
        Screen.__init__(self, background_image_name="brick_img/brick-background.png")

        self.boot_color = None
        self.main_screen = main_screen

        self.totem = MoodTotem()
        self.add_ui_element(self.totem, (100, 75))

        self.add_ui_element(Button("Back", on_click=self.back, size=(140, 30)), (10, 440))

        self.add_ui_element(Button("Done", on_click=self.done_with_reading, size=(140, 30)), (160, 440))

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
        Screen.on_deactivate(self)
        self.change_state(None)

    def back(self, owner):
        self.app.set_current_screen(self.main_screen)

    def done_with_reading(self, owner):
        # todo save reading and display results ?

        self.back(owner)

    def render(self, display):
        Screen.render(self, display)
        # if self.current_color > -1:
        #     display.blit(bricks[self.current_color], (50, 50))
        if self.state is not None:
            self.state.render(display)