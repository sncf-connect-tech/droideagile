import logging

import pygame
from pygame import mixer, MOUSEBUTTONDOWN
from pygame.constants import QUIT

from app.droid_configuration import init_configuration, droidConfig


# a basic screen
class Screen:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def render(self, display):
        pass

    def on_event(self, event, mouse_pos):
        self.log.debug("got event " + str(event) + " at " + str(mouse_pos))
        return self


# a pygame app
class App:
    def __init__(self, startup_screen, app_name="App"):
        self.current_screen = startup_screen

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Starting app %s" % app_name)

        # load configuration
        init_configuration()

        # init pygame
        pygame.init()
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
            self.surface.fill((100, 255, 255))

            # render current screen
            self.current_screen.render(self.surface)

            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == MOUSEBUTTONDOWN:
                    # compute mouse position given rotation
                    # bon ca marche pas bien mais bon... ca marche que avec 270....
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rotation != 0:
                        pos = rotate((0, 0), (mouse_pos[0],-mouse_pos[1]), math.radians(self.rotation))
                        pos = (self.real_height  + pos[0], -pos[1])
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
