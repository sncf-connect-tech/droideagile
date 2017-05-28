import logging

import pygame
from pygame import mixer, MOUSEBUTTONDOWN, MOUSEMOTION, BLEND_RGBA_MULT
from pygame.constants import QUIT

from app.droid_configuration import init_configuration, droidConfig, path_to_image

# load configuration
init_configuration()

# init pygame
pygame.init()

# fonts
font = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_smaller = pygame.font.Font(None, 20)


# basic graphical element
class Element:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def render(self, display):
        pass

    def on_event(self, event, mouse_pos):
        self.log.debug("got event " + str(event) + " at " + str(mouse_pos))
        return self


# a basic button
class Button(Element):
    def __init__(self, text, position=(0, 0), size=(300, 50)):
        Element.__init__(self)
        self.state = "idle"
        self.width = size[0]
        self.height = size[1]
        self.position = position
        self.surface = pygame.Surface((self.width, self.height))

        txt_width, txt_height = font.size(text)
        xoffset = (self.width - txt_width) // 2
        yoffset = (self.height - txt_height) // 2
        self.txt_position = position[0] + xoffset, position[1] + yoffset

        self.text_surface = font_small.render(text, True, (255, 255, 255))

    def on_event(self, event, mouse_pos):
        if self.surface.get_rect().move(self.position).collidepoint(mouse_pos):
            if event.type == MOUSEMOTION and self.state != "active":
                self.state = "hover"
            elif event.type == MOUSEBUTTONDOWN:
                if self.state == "active":
                    self.state = "idle"
                else:
                    self.state = "active"
        else:
            if self.state != "active":
                self.state = "idle"

    def render(self, display):
        Element.render(self, display)
        # self.log.debug("button state " + self.state)
        if self.state == "idle":
            self.surface.fill((100, 100, 200))
        elif self.state == "hover":
            self.surface.fill((150, 150, 255))
        elif self.state == "active":
            self.surface.fill((255, 140, 140))
        display.blit(self.surface, self.position, None, BLEND_RGBA_MULT)
        display.blit(self.text_surface, self.txt_position)


# a basic screen
class Screen(Element):
    def __init__(self, background_image_name=None):
        Element.__init__(self)
        self.elements = []
        if background_image_name is not None:
            self.background = pygame.image.load(path_to_image(background_image_name))

    def add_ui_element(self, ui_element):
        self.elements.append(ui_element)

    def render_background(self, display):
        if self.background is not None:
            display.blit(self.background, (0, 0))

    def render_elements(self, display):
        Element.render(self, display)
        for element in self.elements:
            element.render(display)

    def render(self, display):
        Element.render(self, display)
        self.render_background(display)
        self.render_elements(display)

    def on_event(self, event, mouse_pos):
        for element in self.elements:
            element.on_event(event, mouse_pos)
        return self

    def set_up(self):
        # usable fonts
        self.font_small = pygame.font.Font(None, 30)


# a pygame app
class App:
    def __init__(self, startup_screen, app_name="App"):
        self.current_screen = startup_screen

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Starting app %s" % app_name)

        self.clock = pygame.time.Clock()

        self.real_width = droidConfig.getint("Screen", "RealWidth")
        self.real_height = droidConfig.getint("Screen", "RealHeight")
        self.rotation = droidConfig.getint("Screen", "Rotation")
        self.use_full_screen = droidConfig.getboolean("Screen", "UseFullScreen")
        self.hide_mouse = droidConfig.getboolean("Screen", "HideMouse")

        # actual display
        self.display = pygame.display.set_mode((self.real_width, self.real_height),
                                               pygame.FULLSCREEN if self.use_full_screen else 0)
        # working display
        # it is a surface like display but rotated
        self.surface = pygame.transform.rotate(self.display, self.rotation)
        self.logger.debug("center of new surface : " + str(self.surface.get_rect().center) + " rect is " + str(
            self.surface.get_rect()))
        pygame.mouse.set_visible(not self.hide_mouse)

        # init sound system
        mixer.init()

        self.logger.info("App ready to display")

    # main loop here
    def run(self):
        self.logger.debug("Running app")

        # set up app here
        self.set_up()

        done = False
        while not done:

            # clear screen
            self.surface.fill((255, 255, 255))

            # render current screen
            self.current_screen.render(self.surface)

            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == MOUSEBUTTONDOWN or MOUSEMOTION:
                    # compute mouse position given rotation
                    # bon ca marche pas bien mais bon... ca marche que avec 270....
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rotation != 0:
                        pos = rotate((0, 0), (mouse_pos[0], -mouse_pos[1]), math.radians(self.rotation))
                        pos = (self.real_height + pos[0], -pos[1])
                    else:
                        pos = mouse_pos

                    # pass event to current_screen
                    new_screen = self.current_screen.on_event(event, pos)
                    self.current_screen = new_screen

            # tick to 60 fps
            self.clock.tick(60)

            # rotate surface
            rotated = pygame.transform.rotate(self.surface, -self.rotation)

            self.display.blit(rotated, (0, 0))

            # flip to the screen
            pygame.display.flip()

        self.logger.debug("Stopping app")
        # clean up app here
        self.clean_up()
        self.logger.debug("Exiting app")

    def clean_up(self):
        pygame.quit()

    def set_up(self):
        pass


import math


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy
