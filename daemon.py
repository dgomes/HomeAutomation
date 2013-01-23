#!/usr/bin/env python
import httplib
import yaml
import sys
import urllib2
from os import path
from datetime import datetime
import calendar

from serial.serialutil import SerialException

from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.serialport import SerialPort
from twisted.web import server, resource
from twisted.python import log

import json

import sony
import chacon

serial = False
conf = yaml.load(file('settings.yaml', 'r'))
log.startLogging(sys.stdout)
#log.startLogging(open(conf['logfile'], 'w'))

class USBClient(LineOnlyReceiver):
	def __init__(self, callback):
		self.lastread = calendar.timegm(datetime.utcnow().utctimetuple())
		self.lastline = ""
		self.same = 0
		self.callback = callback

	def connectionFailed(self):
		print "Connection Failed:", self
		reactor.stop()

	def lineReceived(self, line):
		print "RCV: ", repr(line)
		if repr(line) == self.lastline:	
			self.same+=1
		else:
			self.same = 0
		
		if self.same > 2 and calendar.timegm(datetime.utcnow().utctimetuple()) - self.lastread > 20:	
			self.callback(line)

		self.lastread = calendar.timegm(datetime.utcnow().utctimetuple())
		self.lastline = repr(line)

	def sendLine(self, cmd):
		print "SEND: ", cmd
		self.transport.write(cmd + "\r\n")

	def outReceived(self, data):
		print "outReceived! with %d bytes!" % len(data)
		self.data = self.data + data

class InfoResource(resource.Resource):
	def getChild(self, name, request):
		print "Name: ", name
		print "Request: ", request
		return self

	def render_GET(self, request):
		return "<html>Info</html>"

class IRCommandResource(resource.Resource):
	isLeaf = True
	def render_GET(self, request):
		command = request.path.split('/')
		print command
		try:
			cmd = sony.codes[command[2]]
			serial.writeSomeData(cmd)
		except:
			log.err()
			return "<html>IR Failed</html>"
		return "<html>IR Command!</html>"

class RFCommandResource(resource.Resource):
	isLeaf = True
	def render_GET(self, request):
		command = request.path.split('/')
		try:
			cmd = chacon.codes[command[2]][command[3]]
			serial.writeSomeData(cmd)
		except:
			log.err()
			return "<html>RF Failed</html>"
		return "<html>RF Sent!</html>"

class WeatherCommandResource(resource.Resource):
	isLeaf = True
	def render_GET(self, request):
		return "<html>Weather Station</html>"


def updateCOSM(line):
	try:
		d = json.loads(line)
	except:
		return

	if d[u'code'] != 100:  #we only care for weather station reports (code 100)
		return
	datastream = json.dumps({"version": "1.0.0", "datastreams": [ { "id": "humidity", "current_value": d[u'Humidity'] }, {"id": "temperature", "current_value": d[u'Temperature'] }]})
	headers = {"Content-type": "text/json", "X-ApiKey": conf['cosm']['ApiKey']}

	try:
		conn = httplib.HTTPConnection("api.cosm.com")
		conn.request("PUT", "/v2/feeds/"+str(conf['cosm']['feed']), datastream, headers)
		if conn.getresponse().status == 200:
			print "COSM update SUCCESSFULY"
		else:
			print "COSM updaye FAILED!"
	except:
		log.err()

if __name__ == "__main__":
	root = InfoResource()
	root.putChild("IR", IRCommandResource())
	root.putChild("RF", RFCommandResource())
	root.putChild("Weather", WeatherCommandResource())
	reactor.listenTCP(conf['port'], server.Site(root))
	try:
		serial = SerialPort(USBClient(updateCOSM), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
	except SerialException as e:
		log.err()
	reactor.run()
