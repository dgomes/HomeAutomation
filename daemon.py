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
from twisted.web import server, resource, static
from twisted.python import log

import json

import sony
import chacon

serial = False
conf = yaml.load(file('settings.yaml', 'r'))
log.startLogging(sys.stdout)
#log.startLogging(open(conf['logfile'], 'w'))

def jsonpCallback(request, data):
	callback = request.args.get('callback')

	if callback: 
		callback = callback[0] 
		data = '%s(%s);' % (callback, data) 
		return data
	return "callback({'error': 'no callback defined'})"

class USBClient(LineOnlyReceiver):
	def __init__(self, callback):
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
			return jsonpCallback(request, "{ 'result': 400 }")
		return jsonpCallback(request, "{ 'result': 200 }")

class RFCommandResource(resource.Resource):
	isLeaf = True
	def render_GET(self, request):
		command = request.path.split('/')
		try:
			cmd = chacon.codes[command[2]][command[3]]
			serial.writeSomeData(cmd)
		except:
			log.err()
			return jsonpCallback(request, "{ 'result': 400 }")
		return jsonpCallback(request, "{ 'result': 200 }")

class WeatherCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self):
		self.data = {'timestamp':0, 'humidity':0, 'indoor_temp':0, 'outdoor_temp':0} 
	def render_GET(self, request):
		data = json.dumps({"humidity": self.data['humidity'], "indoor_temp": self.data['indoor_temp'], "outdoor_temp": self.data['outdoor_temp'] })
		return jsonpCallback(request, data)

	def updateData(self, line):
		try:
			d = json.loads(line)
			if d[u'code'] != 100:  #we only care for weather station reports (code 100)
				return
		except:
			return

		# make sure we are in the same sample acquisition window, else we start from 0	
		if calendar.timegm(datetime.utcnow().utctimetuple()) - self.data['timestamp'] < 5:
			if self.data['humidity'] == d[u'Humidity'] and self.data['indoor_temp'] ==  d[u'IndoorTemperature'] and self.data['outdoor_temp'] == d[u'OutdoorTemperature']:
				self.samples+=1 	
			else:
				self.samples-=1
		else:
			self.samples = 0
		
		# we don't have enough samples so we take a new measure
		if self.samples < 1:	
			self.data['humidity'] = d[u'Humidity']
			self.data['indoor_temp'] =  d[u'IndoorTemperature']
			self.data['outdoor_temp'] = d[u'OutdoorTemperature']
			self.samples+=1
		self.data['timestamp'] = calendar.timegm(datetime.utcnow().utctimetuple())

		# 3 consistent samples? lets publish this stuff!
		if self.samples == 3:
			self.updateCOSM()

	def updateCOSM(self):
		datastream = json.dumps({"version": "1.0.0", "datastreams": [ { "id": "humidity", "current_value": self.data['humidity'] }, {"id": "indoor_temp", "current_value": self.data['indoor_temp']}, {"id": "outdoor_temp", "current_value": self.data['outdoor_temp'] }]})
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
	root = static.File('.')
	root.putChild("IR", IRCommandResource())
	root.putChild("RF", RFCommandResource())
	weather = WeatherCommandResource()
	root.putChild("Weather", weather)
	reactor.listenTCP(conf['port'], server.Site(root))
	try:
		serial = SerialPort(USBClient(weather.updateData), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
	except SerialException as e:
		log.err()
	reactor.run()
