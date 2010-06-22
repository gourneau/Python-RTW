""" receiving OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation

"""

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
        
import OSC
import time, threading

receive_address = '', 9000

# OSC Server. there are three different types of server. 
s = OSC.OSCServer(receive_address) # basic

# this registers a 'default' handler (for unmatched messages), 
s.addDefaultHandlers()

# define a message-handler function for the server to call.
def printing_handler(addr, tags, stuff, source):
    print "---"
    print "received new osc msg from %s" % OSC.getUrlStr(source)
    print "with addr : %s" % addr
    print "typetags %s" % tags
    print "data %s" % stuff
    print "---"
    d = {}
    addr = addr.replace('/1/','')
    d[addr] = stuff[0]
    conn.send(simplejson.dumps(d), destination='/topic/test')

s.addMsgHandler("/print", printing_handler) # adding our function
s.addMsgHandler("/1/push1", printing_handler) # adding our function
s.addMsgHandler("/1/push2", printing_handler) # adding our function
s.addMsgHandler("/1/push3", printing_handler) # adding our function
s.addMsgHandler("/1/push4", printing_handler) # adding our function
s.addMsgHandler("/1/push5", printing_handler) # adding our function
s.addMsgHandler("/1/push6", printing_handler) # adding our function
s.addMsgHandler("/1/push7", printing_handler) # adding our function
s.addMsgHandler("/1/push8", printing_handler) # adding our function
s.addMsgHandler("/1/push9", printing_handler) # adding our function
s.addMsgHandler("/1/push10", printing_handler) # adding our function
s.addMsgHandler("/1/push11", printing_handler) # adding our function
s.addMsgHandler("/1/push12", printing_handler) # adding our function

s.addMsgHandler("/1/fader1", printing_handler) # adding our function
s.addMsgHandler("/1/fader2", printing_handler) # adding our function

# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = s.serve_forever )
st.start()

try :
    while 1 :
        time.sleep(5)

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    s.close()
    print "Waiting for Server-thread to finish"
    st.join() ##!!!
    conn.disconnect()
    print "Done"
        
