#!/usr/bin/env python
import logging
import yaml
import sys
from serial.serialutil import SerialException

from twisted.application import service, internet
from twisted.internet.serialport import SerialPort
from twisted.web import server, static
from twisted.python import log
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

from notify import *
from system import *
from airport import *
from weather import *
from upnp import *
from imeter import *
from sony import *
from chacon import *
from arduino import *
from xivelyInterface import *
from greenhouse import *

conf = yaml.load(file('settings.yaml', 'r'))

def getWebService():
	root = static.File('.')

	xively = XivelyInterface(conf)
	weather = WeatherResource(xively, conf)
	try:
		serial = SerialPort(USBClient(weather.updateData), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
		ir = IRCommandResource(serial)
		rf = RFCommandResource(serial)
		root.putChild("IR", ir)
		root.putChild("RF", rf)
		root.putChild("Weather", weather)
	except SerialException as e:
		log.err()

	greenhouse = GreenHouseResource(xively, conf)
	root.putChild("greenhouse", greenhouse)
	imeter = IMeterResource(xively, conf)
	root.putChild("imeter", imeter)
	igd = UPnPResource(xively, conf)
	root.putChild("igd", igd)
	airport = AirportResource(xively, conf)
	root.putChild("airport", airport)
	system = SystemResource()
	root.putChild("system", system)
	notify = NotifyResource(conf)
	root.putChild("notify", notify)

	return internet.TCPServer(conf['port'], server.Site(root))

application = service.Application(conf['appname'])
logfile = DailyLogFile(conf['appname']+".log", conf['logdir'])
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)

service = getWebService()
service.setServiceParent(application)
