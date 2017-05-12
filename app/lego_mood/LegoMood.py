#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

from datetime import *

import os
from pygame.locals import *

from BrickPi_mock import *  # import BrickPi.py file to use BrickPi operations
from droid_screen import *

from droid_database import *

def load_image(image_name):
    return pygame.image.load(os.path.join(get_droide_dir(), 'images', image_name))


def find_index_of_max(sampling_data):
    col = 0
    winner_index = 0
    for i in range(0, 7):
        if sampling_data[i] > col:
            col = sampling_data[i]
            winner_index = i
    return winner_index


def end():
    pygame.quit()


def print_to_screen(texte, y_offset=0):
    print(texte)
    # screen.clear()
    txt_surf = font.render(texte, True, (125, 125, 125))
    screen.main_panel.blit(txt_surf, (50, 10 + y_offset * font.get_height()))


class MoodElement(object):
    def __init__(self, index):
        super(MoodElement, self).__init__()
        self.index = index

    def value(self):
        return all_values[self.index]


class Mood(object):
    def __init__(self):
        super(Mood, self).__init__()
        self.elements = []

    def add_mood(self, index):
        e = MoodElement(index)
        if e.value() > 0:
            self.elements.append(e)

    def blit(self, screen, pos):
        for ix, element in enumerate(self.elements):
            screen.blit(bricks[element.index], (pos[0], pos[1] + (ix * 25)))
            v = font_small.render(str(element.value()), True, (200, 255, 200))
            screen.blit(v, (pos[0] + 30, pos[1] + (ix * 25)))

    def mean(self):
        return sum(map(lambda e: e.value(), self.elements)) / len(self.elements)

    def count(self):
        return len(self.elements)


#################################################################


screen = DroidScreen(use_full_screen=False)

font = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)

print_to_screen("Startup")

# setup brick pi
BrickPiSetup()  # setup the serial port for communication

all_colors = ["black", "blue", "green", "yellow", "red", "white", "brown"]
all_values = [0, 4, 5, 3, 1, 2, 0]


def load_colors(all_colors):
    return map(lambda color_name: pygame.Color(color_name), all_colors)


def load_images(all_colors):
    return map(lambda color_name: load_image('brick_img/brick-' + color_name + '.png'), all_colors)


colors = load_colors(all_colors)
bricks = load_images(all_colors)

BrickPi.SensorType[PORT_4] = TYPE_SENSOR_EV3_COLOR_M2  # Set the type of sensor at PORT_4.  M2 is Color.
# There's often a long wait for setup with the EV3 sensors.  (1-5 seconds)

port_nb = PORT_4
# tell user which port to use and give a short time to read
print(("EV3 Color sensor should be in PORT {}".format(port_nb + 1)))

result = BrickPiSetupSensors()  # Send the properties of sensors to BrickPi.  Set up the BrickPi.
print("sensors setup result = " + str(result))
if result != 0:
    sys.exit()

print_to_screen("sensors are up")

# initialisation du systeme d'echantillonage.
sampling_data = [0] * 7
sampling_start_time = datetime.now()
sampling_max_seconds = 1
idle_max_seconds = 1
display_max_seconds = 1

print_to_screen("warming up")
# warm up pour determiner la color de boot (quand y a rien devant)
for i in range(0, 100):
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result:
        color_sensor = BrickPi.Sensor[port_nb]
        if color_sensor < 7:
            sampling_data[color_sensor - 1] += 1
    time.sleep(.01)  # sleep for 10 ms

boot_color = find_index_of_max(sampling_data)

print("warm up done: " + str(sampling_data))
print("color is " + str(colors[boot_color]) + "," + str(boot_color), 1)

# state machine:

#
# idle  -------> sampling -----> display
#   ^                               |
#   +-------------------------------+
#
#

sampling_state = 'idle'
idle_start_time = datetime.now()

##
##
mood_counter = 0

idle_text = font.render("En Attente...", True, (125, 255, 100))
sampling_text = font.render("Lecture...", True, (200, 255, 200))
display_text = font.render("Ok !", True, (20, 255, 100))
state_text = idle_text
state_back = pygame.Surface((DroidScreen.h, idle_text.get_height() + 6))
state_back.fill((200, 200, 200))

control_surface = pygame.Surface((100, 100))

# draw background:
bck_img = load_image('brick_img/brick-background.png')
background = pygame.Surface((DroidScreen.h, DroidScreen.w))
for i in range(0, 13):
    for j in range(0, 20):
        background.blit(bck_img, (i * 25, j * 25))

sprint_number_text = font.render("Sprint " + str(config.config_data.sprint_number), True, (125, 255, 100))

mood = Mood()

carryOn = True

while carryOn:  # main game loop

    screen.clear((0, 0, 0))
    screen.blit(background, (0, 0))

    screen.blit(sprint_number_text, (10, 300))

    screen.blit(state_back, (0, 0), BLEND_RGBA_MULT)
    screen.blit(state_text, state_text.get_rect(center=(DroidScreen.h / 2, 18)))

    mood.blit(screen, (25, 50))

    if sampling_state == "done":
        mean = font_small.render("Mood mean = " + str(mood.mean()), True, (200, 255, 200))
        screen.blit(mean, (50, 200))

        total = font_small.render("Mood count = " + str(mood.count()), True, (200, 255, 200))
        screen.blit(total, (50, 220))

    else:
        result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
        if not result:
            color_sensor = BrickPi.Sensor[port_nb]
            if color_sensor < 7:

                if sampling_state == 'idle':

                    # print ("while idle: " + str(color_sensor) + " boot color: " + str(boot_color))
                    sampling_data[color_sensor - 1] += 1

                    duration = datetime.now() - idle_start_time
                    if duration.total_seconds() >= idle_max_seconds:
                        # trouve la couleur la plus présente pendant la session idle
                        idle_color = find_index_of_max(sampling_data)

                        if idle_color != boot_color:
                            # on doit démarrer une session d'echantillonnage:
                            print("start sampling...")
                            sampling_state = 'sampling'
                            state_text = sampling_text
                            sampling_data = [0] * 7
                            sampling_start_time = datetime.now()
                        else:
                            sampling_data = [0] * 7
                            idle_start_time = datetime.now()

                if sampling_state == 'sampling':

                    # si on est sur une session d'echantillonnage, alors on attend et on capture
                    # des donnees.
                    # incremente la table d'echantillonnage
                    sampling_data[color_sensor - 1] += 1

                    # affiche la couleur en cours de lecture pour controle:
                    current_color = colors[find_index_of_max(sampling_data)]
                    control_surface.fill(current_color)
                    screen.blit(control_surface, (100, 100))

                    # test si on est a la fin de la session
                    duration = datetime.now() - sampling_start_time
                    if duration.total_seconds() >= sampling_max_seconds:
                        print("sampling session ended...")
                        print("sampling data: " + str(sampling_data))

                        # fin de session
                        # prend la valeur max des couleurs pour trouver celle qu'on veut
                        index = find_index_of_max(sampling_data)
                        actual_color = colors[index]
                        # reset state
                        sampling_state = 'display'
                        state_text = display_text
                        display_start_time = datetime.now()
                        sampling_data = [0] * 7

                        print("display color " + str(actual_color))
                        mood_counter += 1
                        # save mood:
                        mood.add_mood(index)

                if sampling_state == "display":
                    duration = datetime.now() - display_start_time
                    if duration.total_seconds() >= display_max_seconds:
                        print("going idle")
                        sampling_state = 'idle'
                        state_text = idle_text
                        sampling_data = [0] * 7
                        idle_start_time = datetime.now()
                        #        DISPLAYSURF.fill(colors[boot_color])

    time.sleep(.001)  # sleep for 10 ms
    # The color sensor will go to sleep and not return proper values if it is left for longer than 100 ms.  You must be sure to poll the color sensor every 100 ms!

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and sampling_state != "done":
            sampling_state = "done"

        elif sampling_state == "done" and (
                            event.type == QUIT or event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN):
            carryOn = False

    screen.flip()

end()
