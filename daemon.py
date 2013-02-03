#!/usr/bin/env python
import logging
import yaml
import sys
from serial.serialutil import SerialException

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.web import server, static
from twisted.python import log

from arduino import USBClient
from cosm import CosmInterface
from sony import IRCommandResource
from chacon import RFCommandResource
from weather import WeatherCommandResource
from imeter import IMeterCommandResource

logging.basicConfig(format='%(asctime)-6s [%(name)s] %(message)s',level=logging.ERROR)
log.startLogging(sys.stdout)
#log.startLogging(open(conf['logfile'], 'w'))

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	root = static.File('.')

	cosm = CosmInterface(conf)
	weather = WeatherCommandResource(cosm, conf)
	try:
		serial = SerialPort(USBClient(weather.updateData), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
		ir = IRCommandResource(serial)
		rf = RFCommandResource(serial)
		root.putChild("IR", ir)
		root.putChild("RF", rf)
		root.putChild("Weather", weather)
	except SerialException as e:
		log.err()

	imeter = IMeterCommandResource(cosm, conf)

	reactor.listenTCP(conf['port'], server.Site(root))
	reactor.run()
