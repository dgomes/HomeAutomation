#!/usr/bin/env python
import httplib
import yaml
import sys
import urllib2

from twisted.internet import reactor 
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.serialport import SerialPort 
from twisted.web import server, resource
from twisted.python import log

from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from wokkel.client import XMPPClient
from wokkel.xmppim import RosterClientProtocol, Message

import json

conf = yaml.load(file('settings.yaml', 'r'))
log.startLogging(sys.stdout) 

class USBClient(LineOnlyReceiver):

	def __init__(self, callback):
		self.usb_list = []
		self.callback = callback

	def connectionFailed(self):
		print "Connection Failed:", self
		reactor.stop()

	def lineReceived(self, line):
		print "RCV: ", repr(line)
		self.callback(line)

	def sendLine(self, cmd):
		print "SEND: ", cmd
		self.transport.write(cmd + "\r\n")

	def outReceived(self, data):
		print "outReceived! with %d bytes!" % len(data)
		self.data = self.data + data

class CommandResource(resource.Resource):
    isLeaf = True    
    def render_GET(self, request):
	print request
        return "I am a request \n"


def updateCOSM(line):
	try:
		d = json.loads(line)
	except:
		return

	if d[u'code'] != 100:
		return
	datastream = json.dumps({"version": "1.0.0", "datastreams": [ { "id": "humidity", "current_value": d[u'Humidity'] }, {"id": "temperature", "current_value": d[u'Temperature'] }]})
	headers = {"Content-type": "text/json", "X-ApiKey": conf['cosm']['ApiKey']}

	conn = httplib.HTTPConnection("api.cosm.com")
	conn.request("PUT", "/v2/feeds/"+str(conf['cosm']['feed']), datastream, headers)
	print conn.getresponse().status
	print "COSM update"

if __name__ == "__main__":
	reactor.listenTCP(conf['port'], server.Site(CommandResource()))
	SerialPort(USBClient(updateCOSM), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
	reactor.run()
