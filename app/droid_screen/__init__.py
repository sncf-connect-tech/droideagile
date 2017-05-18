import pygame
from pygame import mixer

from app.droid_configuration import droidConfig


class DroidScreen:
    w = 480
    h = 320

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.use_full_screen = droidConfig.getboolean("Screen", "UseFullScreen")
        # load sound tool:
        mixer.init()
        # load display
        self.DISPLAYSURF = pygame.display.set_mode((DroidScreen.w, DroidScreen.h),
                                                   pygame.FULLSCREEN if self.use_full_screen else 0)
        # pygame.mouse.set_visible(False)
        self.main_panel = pygame.Surface((DroidScreen.h, DroidScreen.w))

    def done(self):
        pygame.quit()

    def blit(self, surface, dest, flags=0):
        self.main_panel.blit(surface, dest, area=None, special_flags=flags)

    def clear(self, color=(255, 255, 255)):
        self.main_panel.fill(color)

    # rotate the main panel then update the screen
    def flip(self):
        self.DISPLAYSURF.blit(pygame.transform.rotate(self.main_panel, 90), (0, 0))
        pygame.display.flip()

    def tick(self, fps=0):
        self.clock.tick(fps)

    def hide(self):
        self.DISPLAYSURF = pygame.display.set_mode((DroidScreen.w, DroidScreen.h), pygame.RESIZABLE)

    def restore(self):
        self.DISPLAYSURF = pygame.display.set_mode((DroidScreen.w, DroidScreen.h),
                                                   pygame.FULLSCREEN if self.use_full_screen else 0)
