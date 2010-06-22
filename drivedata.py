#!/usr/bin/env python
#This script requires the following Python modules:
#  pygame   - http://www.pygame.org/

#take care of stomp
import sys
import optparse
import logging
import stomp
import simplejson

try:
        conn = stomp.Connection()
        print "connected to stomp"
        conn.start()
        conn.connect()
except:
        print "could not connect to stomp"
	sys.exit(1)
        

import sys
import pygame

from pygame.locals import *

# allow multiple joysticks
joy = []

# handle joystick event
def handleJoyEvent(e):
    if e.type == pygame.JOYAXISMOTION:
        axis = "unknown"
        if (e.dict['axis'] == 0):
            axis = "X"

        if (e.dict['axis'] == 1):
            axis = "Y"

        if (axis != "unknown"):
            str = "Axis: %s; Value: %f" % (axis, e.dict['value'])
            print str
	    #y axis of the joystick, this controlls the steering
            if (axis == "X"):
		d = {}
		v = (e.dict['value'] + 1) / 2
		if v < 0:
			v = 0
		if v > 1:
			v = 1
		d["fader1"] = v
		conn.send(simplejson.dumps(d), destination='/topic/test')
                pos = e.dict['value']
                # convert joystick position to servo increment, 0-180
    elif e.type == pygame.JOYBUTTONDOWN:
        str = "Button: %d" % (e.dict['button'])
        # Button 0 (trigger) to quit
        if (e.dict['button'] == 0):
            quit()
	    conn.disconnect()
    else:
        pass
    
# wait for joystick input
def joystickControl():
    while True:
	try:
		e = pygame.event.wait()
		if (e.type == pygame.JOYAXISMOTION or e.type == pygame.JOYBUTTONDOWN):
		    handleJoyEvent(e)
	except KeyboardInterrupt:
		print "\nGot keyboard interrupt. Exiting..."
		sys.exit(0)
# main method
def main():
    # initialize pygame
    pygame.joystick.init()
    pygame.display.init()
    if not pygame.joystick.get_count():
        print "\nI could not find a joystick, please plug one in, or un-plug and re-plug back in your current joystick.\n"
        quit()
    print "\n%d joystick detected." % pygame.joystick.get_count()
    for i in range(pygame.joystick.get_count()):
        myjoy = pygame.joystick.Joystick(i)
        myjoy.init()
        joy.append(myjoy)
        print "Joystick %d: " % (i) + joy[i].get_name()
    print "Pull trigger (button 0) to quit.\n"
    # run joystick listener loop
    joystickControl()
    
# allow use as a module or standalone script
if __name__ == "__main__":
    main()
