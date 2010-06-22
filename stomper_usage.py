#!/usr/bin/python

import sys
import optparse
import logging
import stomp

try:
	conn = stomp.Connection()
	print "connected to activemq"
	conn.start()
	conn.connect()
except:
	print "could not connect to activemq"
	
conn.send("{}", destination='/topic/test')

# Todo: Clean up properly.
conn.disconnect()

