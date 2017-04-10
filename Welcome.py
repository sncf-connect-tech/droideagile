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

from droid_screen import DroidScreen
from wall_e import WallE

def end():
    pygame.quit()
    sys.exit()


def shutdown():
    pygame.quit()
    subprocess.call("sudo shutdown --poweroff now", shell=True)


def lego_mood():
    print("lego mood")
    subprocess.call('echo "lego mood activated" | festival --tts -', shell=True)
    subprocess.call("./lego_mood/LegoMood.py")
    print("lego mood done")


def random_picker():
    print("random_picker")
    subprocess.call('echo "random picker activated" | festival --tts -', shell=True)
    subprocess.call("./random_picker/random_picker.py")
    print("random_picker done")


def meeting_timer():
    subprocess.call('echo "meeting timer activated" | festival --tts -', shell=True)
    subprocess.call("./meeting_timer/meeting_timer.py")


def draw_feature(text, pos):
    feature_1_text = font_small.render(text, True, (255, 255, 255))
    feature.fill((100, 100, 255))
    # feature_1.blit(feature_1_text, (10,10))
    screen.main_panel.blit(feature, (10, pos), None, BLEND_RGBA_MULT)
    screen.main_panel.blit(feature_1_text, (20, pos + 15))


def draw_busy(text, pos):
    feature_1_text = font_small.render(text, True, (255, 255, 255))
    feature.fill((255, 140, 140))
    #  feature.blit(feature_1_text, (10,10))
    screen.main_panel.blit(feature, (10, pos), None, BLEND_RGBA_MULT)
    screen.main_panel.blit(feature_1_text, (20, pos + 15))


def exterminate():
    mixer.music.load('./sounds/Exterminate.mp3')
    mixer.music.play()


screen = DroidScreen(use_full_screen=True)

wall_e = WallE()
wall_e_2 = WallE()
all_sprites_list = pygame.sprite.Group()

all_sprites_list.add(wall_e)
all_sprites_list.add(wall_e_2)

wall_e.rect.x = 10
wall_e.rect.y = 10

feature = pygame.Surface((300, 50))

font = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_smaller = pygame.font.Font(None, 20)

# charge une image de fond.
img_back = pygame.image.load(os.path.join('images', 'background2.png'))
startup_text = font.render("Welcome, Droid...", True, (200, 125, 125))

top_panel = pygame.Surface((320, 50))
top_panel.fill((180, 180, 180))

bottom_text = font_smaller.render("Shutdown...", True, (255, 255, 255))
bottom_panel = pygame.Surface((320, 30))
bottom_panel.fill((255, 0, 0))

state = "ready"

while True:  # main game loop

    screen.clear()

    all_sprites_list.update()

    screen.main_panel.blit(img_back, (0, 0))

    wall_e.move(-1)
    wall_e_2.move()

    all_sprites_list.draw(screen.main_panel)

    screen.main_panel.blit(top_panel, (0, 0), None, BLEND_RGBA_MULT)
    screen.main_panel.blit(startup_text, (40, 11))

    screen.main_panel.blit(bottom_panel, (0, 450), None, BLEND_RGBA_MULT)
    screen.main_panel.blit(bottom_text, (10, 458))

    if state == "ready":
        draw_feature("Random Picker", 120)
        draw_feature("Lego Mood", 200)
        draw_feature("Meeting Timer", 280)

    for event in pygame.event.get():
        if event.type == QUIT:
            end()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            end()
        elif event.type == MOUSEBUTTONDOWN and state == "ready":
            pos = pygame.mouse.get_pos()
            x = pos[0]
            y = pos[1]
            if 120 < x < 120 + 50 and 10 < y < 300:
                state = "random_picker"
                draw_busy("Random Picker", 120)

            elif 200 < x < 200 + 50 and 10 < y < 300:
                state = "lego_mood"
                draw_busy("Lego Mood", 200)

            elif 280 < x < 280 + 50:

                state = "meeting_timer"
                draw_busy("Meeting Timer", 280)

            elif 0 < x < 50:

                exterminate()
            elif x > 450:
                shutdown()

    screen.tick(60)
    screen.flip()

    if state != "ready":
        screen.hide()
        if state == "lego_mood":
            lego_mood()
        elif state == "random_picker":
            random_picker()
        elif state == "meeting_timer":
            meeting_timer()
        state = "ready"
        screen.restore()

    pygame.display.flip()
