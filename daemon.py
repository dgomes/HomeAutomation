#!/usr/bin/env python
import logging
import yaml
import sys
from serial.serialutil import SerialException

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.web import server, static
from twisted.python import log

from snmp import *
from weather import *
from upnp import *
from imeter import *
from sony import *
from chacon import *
from arduino import *
from cosm import *

logging.basicConfig(format='%(asctime)-6s [%(name)s] %(message)s',level=logging.ERROR)
log.startLogging(sys.stdout)
#log.startLogging(open(conf['logfile'], 'w'))

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	root = static.File('.')

	cosm = CosmInterface(conf)
	weather = WeatherResource(cosm, conf)
	try:
		serial = SerialPort(USBClient(weather.updateData), conf['serial']['port'], reactor, baudrate=conf['serial']['baudrate'])
		ir = IRCommandResource(serial)
		rf = RFCommandResource(serial)
		root.putChild("IR", ir)
		root.putChild("RF", rf)
		root.putChild("Weather", weather)
	except SerialException as e:
		log.err()

	imeter = IMeterResource(cosm, conf)
	root.putChild("imeter", imeter)
	igd = UPnPResource(cosm, conf)
	root.putChild("igd", igd)
	airport = SNMPResource(cosm, conf)
	root.putChild("airport", airport)

	reactor.listenTCP(conf['port'], server.Site(root))
	reactor.run()
