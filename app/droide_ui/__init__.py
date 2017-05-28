import logging
from pygame import mixer

import pygame
from pygame.constants import QUIT

from app.droid_configuration import init_configuration, droidConfig


# a basic screen
class Screen:
    def __init__(self):
        pass


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

        self.width = droidConfig.getint("Screen","Width")
        self.height = droidConfig.getint("Screen","Height")
        self.rotation = droidConfig.getint("Screen", "Rotation")
        self.use_full_screen = droidConfig.getboolean("Screen", "UseFullScreen")
        self.hide_mouse = droidConfig.getboolean("Screen", "HideMouse")

        self.display = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN if self.use_full_screen else 0)
        pygame.mouse.set_visible(not self.hide_mouse)

        # init sound system
        mixer.init()

        self.logger.info("App ready to display")


    # main loop here
    def run(self):
        logging.debug("Running app")

        # set up app here
        self.set_up()

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True

        logging.debug("Stopping app")
        # clean up app here
        self.clean_up()
        logging.debug("Exiting app")

    def clean_up(self):
        pygame.quit()

    def set_up(self):
        pass
