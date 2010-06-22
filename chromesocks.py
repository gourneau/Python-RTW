#!/usr/bin/python

"""
this looks for data, then stuffs the values into
JSON and pushes the JSON to a web app using websockets.

This needs twisted svn branch
http://twistedmatrix.com/trac/browser/branches/websocket-4173?rev=27790

stomper examples : http://stomper.googlecode.com/svn/trunk/lib/stomper/examples/receiver.py

"""

from twisted.internet import reactor, interfaces, protocol
from twisted.protocols import basic
from twisted.web import server, resource
from twisted.web.static import File
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.protocol import Factory

from twisted.internet import reactor
from twisted.web.websocket import WebSocketHandler, WebSocketSite
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet.task import LoopingCall
from twisted.python import log
import sys

import simplejson

import logging

#start the ws blasting thing
instances = []

class Echohandler(WebSocketHandler):
    def frameReceived(self, frame):
        log.msg("Received frame '%s'" % frame)
        self.transport.write(frame + "\n")

def echo_factory(request):
    instance = Echohandler(request)
    instances.append(instance)
    #the instances need to be removed when a client disconnects
    #request.notifyFinish().addCallback(lambda x: instances.remove(instance))
    return instance

def socket_blast(val):
    """send the data to all open websockets"""
    for instance in instances:
        instance.transport.write(val + "\n")


###################stomp#########################

from twisted.internet.protocol import Protocol, ReconnectingClientFactory

import stomper

stomper.utils.log_init(logging.DEBUG)

DESTINATION="/topic/test"

class MyStomp(stomper.Engine):
    
    def __init__(self, username='', password=''):
        super(MyStomp, self).__init__()
        self.username = username
        self.password = password
        self.log = logging.getLogger("receiver")


    def connect(self):
        """Generate the STOMP connect command to get a session.
        """
        return stomper.connect(self.username, self.password)


    def connected(self, msg):
        """Once I've connected I want to subscribe to my the message queue.
        """
        super(MyStomp, self).connected(msg)

        self.log.info("connected: session %s" % msg['headers']['session'])
        f = stomper.Frame()
        f.unpack(stomper.subscribe(DESTINATION))
        return f.pack()

        
    def ack(self, msg):
        """Process the message and determine what to do with it.
        """
        self.log.info("RECEIVER - received: %s " % msg['body'])
        print msg['body']
        socket_blast(msg['body'])
        print(msg['body'])
        
#        return super(MyStomp, self).ack(msg) 

        return stomper.NO_REPONSE_NEEDED
        

class StompProtocol(Protocol):

    def __init__(self, username='', password=''):
        self.sm = MyStomp(username, password)


    def connectionMade(self):
        """Register with the stomp server.
        """
        cmd = self.sm.connect()
        self.transport.write(cmd)

    
    def dataReceived(self, data):
        """Data received, react to it and respond if needed.
        """
        msg = stomper.unpack_frame(data)
        returned = self.sm.react(msg)
        if returned:
            self.transport.write(returned)


class StompClientFactory(ReconnectingClientFactory):
    
    # Will be set up before the factory is created.
    username, password = '', ''
    
    def startedConnecting(self, connector):
        """Started to connect.
        """

    def buildProtocol(self, addr):
        """Transport level connected now create the communication protocol.
        """
        return StompProtocol(self.username, self.password)
    
    
    def clientConnectionLost(self, connector, reason):
        """Lost connection
        """
        print 'Lost connection.  Reason:', reason
    
    
    def clientConnectionFailed(self, connector, reason):
        """Connection failed
        """
        print 'Connection failed. Reason:', reason        
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

################################################end stomp

def main():

    log.startLogging(sys.stdout)
    root = File(".")
    site = WebSocketSite(root)
    site.addHandler("/ws/echo", echo_factory)
    reactor.listenTCP(8080, site)

    #listen to stomp
    reactor.connectTCP('localhost', 61613, StompClientFactory())
    reactor.run()
    
if __name__ == "__main__":
    main()
