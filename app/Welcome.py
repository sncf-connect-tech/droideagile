#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import os
import pygame
import subprocess
import sys
from pygame import mixer
from pygame.locals import *

from app.droid_configuration import config

from app.droid_screen import DroidScreen
from wall_e import WallE


class App:
    def __init__(self):

        use_full_screen = config().getboolean("Screen", "UseFullScreen")
        self.screen = DroidScreen(use_full_screen)
        self.feature = pygame.Surface((300, 50))
        self.font = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 30)
        self.font_smaller = pygame.font.Font(None, 20)

    def end(self):
        pygame.quit()
        sys.exit()

    def shutdown(self):
        pygame.quit()
        subprocess.call("sudo shutdown --poweroff now", shell=True)

    def lego_mood(self):
        print("lego mood")
        subprocess.call('echo "lego mood activated" | festival --tts -', shell=True)
        subprocess.call("./lego_mood/LegoMood.py")
        print("lego mood done")

    def random_picker(self):
        print("random_picker")
        subprocess.call('echo "random picker activated" | festival --tts -', shell=True)
        subprocess.call("./random_picker/random_picker.py")
        print("random_picker done")

    def meeting_timer(self):
        subprocess.call('echo "meeting timer activated" | festival --tts -', shell=True)
        subprocess.call("./meeting_timer/meeting_timer.py")

    def draw_feature(self, text, pos):
        feature_1_text = self.font_small.render(text, True, (255, 255, 255))
        self.feature.fill((100, 100, 255))
        # feature_1.blit(feature_1_text, (10,10))
        self.screen.main_panel.blit(self.feature, (10, pos), None, BLEND_RGBA_MULT)
        self.screen.main_panel.blit(feature_1_text, (20, pos + 15))

    def draw_busy(self, text, pos):
        feature_1_text = self.font_small.render(text, True, (255, 255, 255))
        self.feature.fill((255, 140, 140))
        #  feature.blit(feature_1_text, (10,10))
        self.screen.main_panel.blit(self.feature, (10, pos), None, BLEND_RGBA_MULT)
        self.screen.main_panel.blit(feature_1_text, (20, pos + 15))

    def exterminate(self):
        mixer.music.load('./sounds/Exterminate.mp3')
        mixer.music.play()

    def run(self):

        wall_e = WallE()
        wall_e_2 = WallE()
        all_sprites_list = pygame.sprite.Group()

        all_sprites_list.add(wall_e)
        all_sprites_list.add(wall_e_2)

        wall_e.rect.x = 10
        wall_e.rect.y = 10

        # charge une image de fond.
        img_back = pygame.image.load(os.path.join('images', 'background2.png'))
        startup_text = self.font.render("Welcome, Droid...", True, (200, 125, 125))

        top_panel = pygame.Surface((320, 50))
        top_panel.fill((180, 180, 180))

        bottom_text = self.font_smaller.render("Shutdown...", True, (255, 255, 255))
        bottom_panel = pygame.Surface((320, 30))
        bottom_panel.fill((255, 0, 0))

        state = "ready"

        while True:  # main game loop

            self.screen.clear()

            all_sprites_list.update()

            self.screen.main_panel.blit(img_back, (0, 0))

            wall_e.move(-1)
            wall_e_2.move()

            all_sprites_list.draw(self.screen.main_panel)

            self.screen.main_panel.blit(top_panel, (0, 0), None, BLEND_RGBA_MULT)
            self.screen.main_panel.blit(startup_text, (40, 11))

            self.screen.main_panel.blit(bottom_panel, (0, 450), None, BLEND_RGBA_MULT)
            self.screen.main_panel.blit(bottom_text, (10, 458))

            if state == "ready":
                self.draw_feature("Random Picker", 120)
                self.draw_feature("Lego Mood", 200)
                self.draw_feature("Meeting Timer", 280)

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.end()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.end()
                elif event.type == MOUSEBUTTONDOWN and state == "ready":
                    pos = pygame.mouse.get_pos()
                    x = pos[0]
                    y = pos[1]
                    if 120 < x < 120 + 50 and 10 < y < 300:
                        state = "random_picker"
                        self.draw_busy("Random Picker", 120)

                    elif 200 < x < 200 + 50 and 10 < y < 300:
                        state = "lego_mood"
                        self.draw_busy("Lego Mood", 200)

                    elif 280 < x < 280 + 50:

                        state = "meeting_timer"
                        self.draw_busy("Meeting Timer", 280)

                    elif 0 < x < 50:

                        self.exterminate()
                    elif x > 450:
                        self.shutdown()

            self.screen.tick(60)
            self.screen.flip()

            if state != "ready":
                self.screen.hide()
                if state == "lego_mood":
                    self.lego_mood()
                elif state == "random_picker":
                    self.random_picker()
                elif state == "meeting_timer":
                    self.meeting_timer()
                state = "ready"
                self.screen.restore()

            pygame.display.flip()
