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
import sys
from pygame import mixer  # Load the required library
from pygame.locals import *

mixer.init()

from BrickPi import *  # import BrickPi.py file to use BrickPi operations

BrickPiSetup()  # setup the serial port for communication

wheel_power = 255


def exterminate():
    mixer.music.load('/home/pi/droide/sounds/countdown.mp3')
    mixer.music.play()


def end():
    pygame.quit()
    sys.exit()


def display(text):
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
    pygame.display.set_caption('Meeting Timer')
    timer_font = pygame.font.Font(None, 100)
    text_font = pygame.font.Font(None, 40)
    startup_text = timer_font.render(text, True, (125, 125, 125))
    main_panel = pygame.Surface((320, 480))
    main_panel.fill((0, 0, 0))
    main_panel.blit(startup_text, (20, 100))
    # and blit it to the screen
    newsurf = pygame.transform.rotate(main_panel, 90)
    DISPLAYSURF.blit(newsurf, (0, 0))
    pygame.display.flip()

    return DISPLAYSURF, timer_font, text_font, main_panel


def update_display(DISPLAYSURF, timer_font, text_font, main_panel, text, alert_message):
    main_panel.fill((0, 0, 0))
    if alert_message is not None:
        running_text = text_font.render(alert_message, True, (255, 0, 0))
        main_panel.blit(running_text, (10, 200))
        running_text = timer_font.render(text, True, (255, 0, 0))
    else:
        running_text = timer_font.render(text, True, (125, 125, 125))

    main_panel.blit(running_text, (80, 100))
    newsurf = pygame.transform.rotate(main_panel, 90)
    DISPLAYSURF.blit(newsurf, (0, 0))
    pygame.display.flip()


def rotate_motors(left_wheel_port, right_wheel_port):
    BrickPi.MotorSpeed[left_wheel_port] = -wheel_power
    BrickPi.MotorSpeed[right_wheel_port] = -wheel_power
    BrickPiUpdateValues()


def launch_timer(timer, alert_time):
    mins, secs = divmod(alert_time, 60)
    alert_time_format = '{:02d}:{:02d}'.format(mins, secs)

    mins, secs = divmod(timer, 60)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    # Init display
    DISPLAYSURF, timer_font, text_font, main_panel = display(timeformat)

    keep_alerting = False
    counter = 0
    while timer:
        for event in pygame.event.get():
            if event.type == QUIT:
                end()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                end()

        timer -= 1
        mins, secs = divmod(timer, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        alert_message = None
        if (timeformat == alert_time_format or keep_alerting) and counter < 10:
            alert_message = "Running out of time!"
            rotate_motors(0, 1)
            # Play a sound every 3 s.
            if counter % 3 == 0:
                exterminate()
            keep_alerting = True
        else:
            keep_alerting = False

        if keep_alerting:
            counter += 1

        # Update display of the timer
        update_display(DISPLAYSURF, timer_font, text_font, main_panel, timeformat, alert_message)
        time.sleep(1)

    end_text = "End of meeting!"
    update_display(DISPLAYSURF, text_font, None, main_panel, end_text, None)
    end()


def main(argv):
    args = parse_args(argv)
    BrickPi.MotorEnable[args.left_wheel_port] = 1  # Enable the Motor
    BrickPi.MotorEnable[args.right_wheel_port] = 1  # Enable the Motor

    launch_timer(args.timer, args.alert_time)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Define how to rotate the motors')
    parser.add_argument('--timer', type=int, default=20, help='The timer in seconds')
    parser.add_argument('--alert_time', type=int, default=10, help='The time when alerting in seconds')
    parser.add_argument('--left_wheel_port', type=int, default=0, help='The name of port of the left wheel')
    parser.add_argument('--right_wheel_port', type=int, default=1, help='The name of port of the right wheel')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
