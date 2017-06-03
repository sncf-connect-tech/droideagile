import logging
from os.path import exists

import pygame
import qrcode
from pygame import mixer, MOUSEBUTTONDOWN, MOUSEMOTION, BLEND_RGBA_MULT
from pygame.constants import QUIT

from app.droid_configuration import init_configuration, droidConfig, path_to_image, path_to_tmp_file

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
        self.position = (0, 0)
        self.owner = None

    def enroll(self, position, owner):
        self.owner = owner
        self.position = position

    def render(self, display):
        pass

    def on_event(self, event, mouse_pos):
        pass
        #   self.log.debug("got event " + str(event) + " at " + str(mouse_pos))


# a graphical element that contains others graphical elements
class Container(Element):
    def __init__(self):
        Element.__init__(self)
        self.elements = []

    # def add_ui_element(self, ui_element, centered=False):
    #     self.elements.append(ui_element)
    #     if centered:
    #         ui_element.center_relative_to(self)

    def add_ui_element(self, ui_element, position=(0, 0)):
        self.elements.append(ui_element)
        ui_element.enroll(position, self)

    def render_elements(self, display):
        Element.render(self, display)
        for element in self.elements:
            element.render(display)

    def render(self, display):
        Element.render(self, display)
        self.render_elements(display)

    def on_event(self, event, mouse_pos):
        for element in self.elements:
            element.on_event(event, mouse_pos)


# a basic panel with text
class Panel(Container):
    def __init__(self, text, size=(320, 50)):
        Container.__init__(self)
        self.width = size[0]
        self.height = size[1]
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((180, 180, 180))
        self.txt_width = 0
        self.txt_height = 0
        self.text_surface = None
        self.set_text(text)
        self.txt_position = None

    def enroll(self, position, owner):
        Element.enroll(self, position, owner)
        xoffset = (self.width - self.txt_width) // 2
        yoffset = (self.height - self.txt_height) // 2
        self.txt_position = position[0] + xoffset, position[1] + yoffset

    def render(self, display):
        display.blit(self.surface, self.position, None, BLEND_RGBA_MULT)
        display.blit(self.text_surface, self.txt_position)
        Container.render(self, display)

    def set_text(self, text):
        self.txt_width, self.txt_height = font.size(text)
        self.text_surface = font.render(text, True, (200, 125, 125))


# a text label
class Label(Element):
    def __init__(self, text, text_font=font_smaller, text_color=(125, 125, 125)):
        Element.__init__(self)
        self.surface = text_font.render(text, True, text_color)

    def render(self, display):
        Element.render(self, display)
        display.blit(self.surface, self.position)


# a QR code
class QrCode(Element):
    def __init__(self, text):
        Element.__init__(self)
        # text to base64:
        b64 = text.encode('base64').rstrip('\n')
        if not exists(path_to_tmp_file('qrcode' + b64 + '.png')):
            self.log.debug("creating a new qrcode for " + path_to_tmp_file('qrcode' + b64 + '.png'))
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,
                border=1,
            )
            qr.add_data(text)
            qr.make(fit=True)
            qr.make_image().save(path_to_tmp_file('qrcode' + b64 + '.png'))

        self.log.debug("loading qrcode from " + path_to_tmp_file('qrcode' + b64 + '.png'))
        self.surface = pygame.image.load(path_to_tmp_file('qrcode' + b64 + '.png'))

    def render(self, display):
        Element.render(self, display)
        display.blit(self.surface, self.position)


# a basic button
class Button(Element):
    def __init__(self, text, on_click=None, size=(300, 50), idle_color=(100, 100, 200), hover_color=(150, 150, 255),
                 active_color=(255, 140, 140), text_font=font_small):
        Element.__init__(self)
        self.active_color = active_color
        self.hover_color = hover_color
        self.idle_color = idle_color
        self.state = "idle"
        self.width = size[0]
        self.height = size[1]
        self.surface = pygame.Surface((self.width, self.height))
        self.txt_width, self.txt_height = text_font.size(text)
        self.text_surface = text_font.render(text, True, (255, 255, 255))
        self.on_click = on_click

    def enroll(self, position, owner):
        Element.enroll(self, position, owner)
        xoffset = (self.width - self.txt_width) // 2
        yoffset = (self.height - self.txt_height) // 2
        self.txt_position = position[0] + xoffset, position[1] + yoffset

    def on_event(self, event, mouse_pos):
        if self.surface.get_rect().move(self.position).collidepoint(mouse_pos):
            if event.type == MOUSEMOTION and self.state != "active":
                self.state = "hover"
            elif event.type == MOUSEBUTTONDOWN:
                if self.state == "active":
                    self.state = "idle"
                else:
                    self.state = "active"
                    if self.on_click is not None:
                        self.on_click(self.owner)
        else:
            self.state = "idle"

    def render(self, display):
        Element.render(self, display)
        # self.log.debug("button state " + self.state)
        if self.state == "idle":
            self.surface.fill(self.idle_color)
        elif self.state == "hover":
            self.surface.fill(self.hover_color)
        elif self.state == "active":
            self.surface.fill(self.active_color)
        display.blit(self.surface, self.position, None, BLEND_RGBA_MULT)
        display.blit(self.text_surface, self.txt_position)


# a basic screen
class Screen(Container):
    def __init__(self, background_image_name=None):
        Container.__init__(self)
        # background management
        if background_image_name is not None:
            self.background = pygame.image.load(path_to_image(background_image_name))
        # navigation management
        self.app = None

    def set_app(self, app):
        self.app = app

    def set_up(self):
        pass

    def render_background(self, display):
        if self.background is not None:
            display.blit(self.background, (0, 0))

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def render(self, display):
        self.render_background(display)
        Container.render(self, display)


# a pygame app
class App:
    def __init__(self, app_name="App"):
        self.current_screen = None
        self.screens = []

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
        for screen in self.screens:
            screen.set_up()

        # check that we have a current_screen to start with
        if self.current_screen is None:
            raise Exception("current_screen should not be none")

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
                    self.current_screen.on_event(event, pos)

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

    def add_screen(self, new_screen):
        self.screens.append(new_screen)
        new_screen.set_app(self)

    def set_current_screen(self, next_screen):
        if self.current_screen is not None:
            self.logger.debug("deactivate " + self.current_screen.__class__.__name__)
            self.current_screen.on_deactivate()
        self.current_screen = next_screen
        self.logger.debug("activate " + self.current_screen.__class__.__name__)
        self.current_screen.on_activate()

    def get_surface_rect(self):
        return self.surface.get_rect()


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
