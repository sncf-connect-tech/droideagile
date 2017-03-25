import pygame
import time
from pygame.constants import *
from random import randint

import droid_screen


class WallE(pygame.sprite.Sprite):
    wall_e_rolling_line_offset = 0
    wall_e_rolling = [(35, 50), (35, 50), (35, 50), (35, 50), (35, 50), (35, 50), (45, 50), (45, 50), (45, 50)]

    def __init__(self):
        # Call the parent class (Sprite) constructor
        super(WallE, self).__init__()

        self.start_frame = time.time()

        self.all_images = pygame.image.load("images/WallE_lowres.png")
        self.all_images.set_colorkey((104, 144, 168))

        self.image = self.all_images.subsurface((0, 0, 35, 50))
        self.rect = pygame.Rect(0, 0, 50, 50)

        self.current_x_offset = 0
        self.current_index = 0

    def move(self):

        # test si on doit changer d'image:
        x = int((time.time() - self.start_frame) * 4 % len(WallE.wall_e_rolling))

        if x != self.current_index:
            # on doit changer de frame
            self.current_index = x

            # on doit trouver l'image suivante:
            if self.current_index == 0:
                self.current_x_offset = 0
            else:
                self.current_x_offset = self.current_x_offset + WallE.wall_e_rolling[self.current_index][0]

            # switch image
            self.image = self.all_images.subsurface((self.current_x_offset, WallE.wall_e_rolling_line_offset,
                                                     WallE.wall_e_rolling[self.current_index][0],
                                                     WallE.wall_e_rolling[self.current_index][1]))
        # switch location
        self.rect.x += 1
        if self.rect.x >= droid_screen.DroidScreen.h:
            self.rect.x = 0
            self.rect.y = randint(0, droid_screen.DroidScreen.w)
