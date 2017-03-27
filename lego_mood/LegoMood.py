#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from builtins import input

from BrickPi import *           #import BrickPi.py file to use BrickPi operations
import pygame, sys
from pygame.locals import *

from datetime import *

import pygame
import time

def find_index_of_max(sampling_data):
    col = 0
    winner_index = 0
    for i in range(0,7) :
       if sampling_data[i] > col :
          col = sampling_data[i]
          winner_index = i
    return winner_index

def end():
    pygame.quit()
    sys.exit()
    
def setup_pygame():
    global DISPLAYSURF
    global main_panel
    
    result = pygame.init()
    print ("init" + str(result))
    result = pygame.display.mode_ok((w, h), pygame.RESIZABLE)
    if result == 0 :
        print ("mode non supporte")
        sys.exit()
    else :
        print ("using color depth of " + str(result))
    #DISPLAYSURF = pygame.display.set_mode((w, h),pygame.RESIZABLE, result)
    DISPLAYSURF = pygame.display.set_mode((w, h),pygame.FULLSCREEN, result)
    #pygame.mouse.set_visible(False)
    pygame.display.set_caption('Lego Mood')
    main_panel = pygame.Surface((h,w))

def blit_to_screen():
    newsurf = pygame.transform.rotate(main_panel, 90)
    DISPLAYSURF.blit(newsurf, (0,0))
    pygame.display.flip()    
        
w = 480
h = 320

setup_pygame()

font = pygame.font.Font(None, 40)
startup_text = font.render("Startup...",True, (125,125,125))
main_panel.blit(startup_text, (50,10))

blit_to_screen()

# setup brick pi
BrickPiSetup()                  # setup the serial port for communication
colors=[pygame.Color("black"),pygame.Color("blue"),pygame.Color("green"),pygame.Color("yellow"),pygame.Color("red"), pygame.Color("white"),pygame.Color("brown")]
colors_2=["brick-black","brick-blue","brick-green","brick-yellow","brick-red","brick-white","brick-brown"]

BrickPi.SensorType[PORT_4] = TYPE_SENSOR_EV3_COLOR_M2   #Set the type of sensor at PORT_4.  M2 is Color.
# There's often a long wait for setup with the EV3 sensors.  (1-5 seconds)

port_nb = PORT_4
# tell user which port to use and give a short time to read
print(("EV3 Color sensor should be in PORT {}".format(port_nb+1)))
time.sleep(0.5)


result = BrickPiSetupSensors()                                  #Send the properties of sensors to BrickPi.  Set up the BrickPi.
print ("sensors setup result = " + str(result))
if result != 0 :
        sys.exit()
time.sleep(0.5)

print("sensors are up")

# initialisation du systeme d'echantillonage.
sampling_data = [0] * 7
sampling_start_time = datetime.now()
sampling_max_seconds = 1
idle_max_seconds = 1
display_max_seconds = 1

print ("warming up")
# warm up pour determiner la color de boot (quand y a rien devant)
for i in range(0,100) :
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result :
        color_sensor = BrickPi.Sensor[port_nb]
        if color_sensor < 7 :
            sampling_data[color_sensor-1] += 1
    time.sleep(.01)     # sleep for 10 ms           

boot_color = find_index_of_max(sampling_data)

print ("warm up done: color is " + str(colors[boot_color]) + "," + str(boot_color))

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

idle_text = font.render("En Attente...",True, (125,255,100))
sampling_text = font.render("Lecture...",True, (200,255,200))
display_text = font.render("Ok !",True, (20,255,100))
state_text = idle_text
state_back = pygame.Surface((idle_text.get_width(),idle_text.get_height()))

control_surface = pygame.Surface((100,100))

while True: # main game loop
        main_panel.blit(state_back, (50,10))
        main_panel.blit(state_text, (50,10))

        result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
        if not result :
                color_sensor = BrickPi.Sensor[port_nb]
                if color_sensor < 7 :

                    if sampling_state == 'idle' : 
                       
                       # print ("while idle: " + str(color_sensor) + " boot color: " + str(boot_color))
                       sampling_data[color_sensor-1] += 1
                     
                       duration = datetime.now() - idle_start_time  
                       if duration.total_seconds() >= idle_max_seconds :                            
                           # trouve la couleur la plus présente pendant la session idle
                           idle_color = find_index_of_max(sampling_data)
                           
                           if idle_color != boot_color :                               
                               # on doit démarrer une session d'echantillonnage:
                               print ("start sampling...")
                               sampling_state = 'sampling'
                               state_text = sampling_text                                                    
                               sampling_data = [0] * 7
                               sampling_start_time = datetime.now()
                           else :
                               sampling_data = [0] * 7
                               idle_start_time = datetime.now()
                        
                    if sampling_state == 'sampling' :
                        
                        # si on est sur une session d'echantillonnage, alors on attend et on capture
                        # des donnees.
                        # incremente la table d'echantillonnage
                        sampling_data[color_sensor-1] += 1

                        # affiche la couleur en cours de lecture pour controle:
                        current_color = colors[find_index_of_max(sampling_data)]
                        control_surface.fill(current_color)
                        main_panel.blit(control_surface, (100,100))
                        
                        # test si on est a la fin de la session
                        duration = datetime.now() - sampling_start_time
                        if duration.total_seconds() >= sampling_max_seconds :
                            print ("sampling session ended...")
                            print ("sampling data: " + str(sampling_data))

                            # fin de session
                            # prend la valeur max des couleurs pour trouver celle qu'on veut
                            index = find_index_of_max(sampling_data)
                            actual_color = colors[index]
                            actual_color_2 = colors_2[index]
                            # reset state 
                            sampling_state = 'display'
                            state_text = display_text 
                            display_start_time = datetime.now()
                            sampling_data = [0] * 7


                            filename = './images/brick_img/'+actual_color_2+'.png'
                            img = pygame.image.load(filename)
                            main_panel.blit(img, (20, 20 + (mood_counter * 25)))
                            pygame.display.flip();
                            
                            
                            print ("display color " + str(actual_color))
                           # pygame.draw.circle(main_panel, actual_color, (20, 20 + (mood_counter * 20)), 10)
                            mood_counter += 1

                            # clean le carré du milieu: todo gerer ça differement.
                            control_surface.fill((0,0,0))
                            main_panel.blit(control_surface, (100,100))
                            
                    if sampling_state == "display" :                         
                        duration = datetime.now() - display_start_time
                        if duration.total_seconds() >= display_max_seconds :
                            print ("going idle")
                            sampling_state = 'idle'  
                            state_text = idle_text     
                            sampling_data = [0] * 7                 
                            idle_start_time = datetime.now()
                    #        DISPLAYSURF.fill(colors[boot_color])
                        
                
        time.sleep(.001)     # sleep for 10 ms
                            # The color sensor will go to sleep and not return proper values if it is left for longer than 100 ms.  You must be sure to poll the color sensor every 100 ms!
        
        for event in pygame.event.get():
                if event.type == QUIT:
                     end()
                elif event.type == MOUSEBUTTONDOWN:
                     end()
                     
        blit_to_screen()
        

