import pygame
import time
from random import randint


class AnimatedSprite(pygame.sprite.Sprite):
    max_move_X = 480
    max_move_Y = 340

    def __init__(self, all_images_path, images_sizes, color_key=(0, 0, 0), animation_frame_rate=4):
        # Call the parent class (Sprite) constructor
        super(AnimatedSprite, self).__init__()

        self.animation_frame_rate = animation_frame_rate
        self.images_sizes = images_sizes
        self.start_frame = time.time()

        self.all_images = pygame.image.load(all_images_path)
        self.all_images.set_colorkey(color_key)

        # load 1st image:
        self.image = self.all_images.subsurface((0, 0, images_sizes[0][0], images_sizes[0][1]))
        self.rect = pygame.Rect(self.image.get_rect())

        self.current_x_offset = 0
        self.current_index = 0

    def move(self, direction=1):

        # test si on doit changer d'image:
        x = int((time.time() - self.start_frame) * self.animation_frame_rate % len(self.images_sizes))

        if x != self.current_index:
            # on doit changer de frame
            self.current_index = x

            # on doit trouver l'image suivante:
            if self.current_index == 0:
                self.current_x_offset = 0
            else:
                self.current_x_offset = self.current_x_offset + self.images_sizes[self.current_index][0]

            # switch image
            self.image = self.all_images.subsurface((self.current_x_offset, WallE.wall_e_rolling_line_offset,
                                                     self.images_sizes[self.current_index][0],
                                                     self.images_sizes[self.current_index][1]))
            # update rect with and height
            self.rect.width = self.images_sizes[self.current_index][0]
            self.rect.height = self.images_sizes[self.current_index][1]

            if direction < 0:
                self.image = pygame.transform.flip(self.image, True, False)

        # switch location
        if direction < 0:
            self.rect.centerx += direction
        else:
            self.rect.centerx += direction
        if self.rect.x >= AnimatedSprite.max_move_X:
            self.rect.x = 0
            self.rect.y = randint(0, AnimatedSprite.max_move_Y)
        elif self.rect.x <= 0:
            self.rect.x = AnimatedSprite.max_move_X
            self.rect.y = randint(0, AnimatedSprite.max_move_Y)


class WallE(AnimatedSprite):
    wall_e_rolling_line_offset = 0
    wall_e_rolling = [(35, 50), (35, 50), (35, 50), (35, 50), (35, 50), (35, 50), (45, 50), (45, 50), (45, 50)]

    def __init__(self):
        # Call the parent class (Sprite) constructor
        super(WallE, self).__init__("app/assets/images/WallE_lowres.png", WallE.wall_e_rolling, (104, 144, 168), animation_frame_rate=3)
