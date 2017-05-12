#!/usr/bin/env python
# Dexter Industries
# Initial Date: June    24, 2013
# Updated: 	 August  13, 2014
# Updated:      Oct     28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This code is for testing the BrickPi with a Lego Motor.
# Connect the LEGO Motors to Motor ports MA,MB, MC and MD.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

# For the code to work - sudo pip install -U future

from __future__ import division
from __future__ import print_function

import argparse
import pygame
import random
import sys
from pygame.locals import *

from BrickPi import *  # import BrickPi.py file to use BrickPi operations

BrickPiSetup()  # setup the serial port for communication

wheel_power = 255
head_power = 255
one_lap_seconds = 10
max_rotate_seconds = 15
change_head_every_seconds = 5

ports = ["PORT_A", "PORT_B", "PORT_C", "PORT_D"]


def end():
    pygame.quit()
    sys.exit()


def display():
    result = pygame.init()
    print("init" + str(result))
    result = pygame.display.mode_ok((480, 320), pygame.FULLSCREEN)
    if result == 0:
        print("mode non supporte")
        sys.exit()
    else:
        print("using color depth of " + str(result))

    DISPLAYSURF = pygame.display.set_mode((480, 320), pygame.FULLSCREEN, result)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('Random Picker')
    font = pygame.font.Font(None, 40)
    startup_text = font.render("Picking someone", True, (125, 125, 125))
    main_panel = pygame.Surface((320, 480))
    main_panel.fill((0, 0, 0))
    main_panel.blit(startup_text, (10, 10))
    # and blit it to the screen
    newsurf = pygame.transform.rotate(main_panel, 90)
    DISPLAYSURF.blit(newsurf, (0, 0))
    pygame.display.flip()

    return DISPLAYSURF, font, main_panel


def update_display(DISPLAYSURF, font, main_panel, text):
    running_text = font.render(text, True, (125, 125, 125))
    main_panel.blit(running_text, (50, 100))
    newsurf = pygame.transform.rotate(main_panel, 90)
    DISPLAYSURF.blit(newsurf, (0, 0))
    pygame.display.flip()


def rotate_motors(direction, left_wheel_port, right_wheel_port, head_port):
    BrickPi.MotorSpeed[left_wheel_port] = wheel_power * direction  # Set the speed of MotorA (-255 to 255)
    BrickPi.MotorSpeed[right_wheel_port] = -wheel_power * direction  # Set the speed of MotorD (-255 to 255)

    maxTime = random.uniform(one_lap_seconds, max_rotate_seconds)
    print('Running for {} seconds'.format(maxTime))
    ot = time.time()

    DISPLAYSURF, font, main_panel = display()

    loading = '.'
    lastSecond = 0
    currentHeadPower = head_power
    while (time.time() - ot < maxTime):
        BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
        currentSecond = int((time.time() - ot))

        # Each second we change the display
        if currentSecond > lastSecond:
            loading += '.'
            update_display(DISPLAYSURF, font, main_panel, loading)


            # Every 5 seconds we change the direction of the head rotation
            BrickPi.MotorSpeed[head_port] = currentHeadPower
            if currentSecond % change_head_every_seconds == 0:
                print ('Change head rotation at {}'.format(currentSecond))
                currentHeadPower = currentHeadPower*(-1)

            lastSecond = currentSecond

    # Quit the random picker
    end()


def main(argv):
    args = parse_args(argv)
    print('Using ports {} and {} for wheels'.format(ports[args.left_wheel_port], ports[args.right_wheel_port]))
    print('Using port {} for head'.format(ports[args.head_port]))
    BrickPi.MotorEnable[args.left_wheel_port] = 1  # Enable the Motor
    BrickPi.MotorEnable[args.right_wheel_port] = 1  # Enable the Motor
    BrickPi.MotorEnable[args.head_port] = 1  # Enable the Motor B

    direction = args.direction
    if direction == 0:
        direction = random.sample([-1, +1], 1)[0]

    stringDirection = 'left' if direction == -1 else 'right'
    print('Running towards {}'.format(stringDirection))

    rotate_motors(direction, args.left_wheel_port, args.right_wheel_port, args.head_port)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Define how to rotate the motors')
    parser.add_argument('--left_wheel_port', type=int, default=0, help='The name of port of the left wheel')
    parser.add_argument('--right_wheel_port', type=int, default=1, help='The name of port of the right wheel')
    parser.add_argument('--head_port', type=int, default=2, help='The name of port of the head motor')
    parser.add_argument('--direction', type=int, default=0, help='The direction positif or negative of rotation')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
