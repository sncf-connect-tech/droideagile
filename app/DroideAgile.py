import pygame

from app.droid_configuration import path_to_image
from app.droide_ui import App, Screen


class MainScreen(Screen):
    def render(self, display):
        display.blit(pygame.image.load(path_to_image("background2.png")),(0,0))
        pygame.draw.rect(display, (200,200,100),(0,0,50,100), 5)



class DroideAgile(App):

    def __init__(self):
        App.__init__(self, MainScreen())
