#!/usr/bin/env python
from datetime import datetime
import calendar
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import QName
import json

import home

from SOAPpy import *
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.web.client import getPage

class UPnPCommandResource(home.Resource):
	def __init__(self, sink, conf):
		self.confid = 'igd'
		self.timestamp = 0
		self.data = {'downloadRate':0, 'inBytes':0, 'uploadRate':0, 'outBytes':0}
		self.upnpc = UPnPClient()
		home.Resource.__init__(self, sink, conf)

	def cronJob(self):
		if self.upnpc.endpoint == None: return
		try:
			rcvd = self.upnpc.GetTotalBytesReceived()
			sent = self.upnpc.GetTotalBytesSent()
			now = calendar.timegm(datetime.utcnow().utctimetuple())
			self.data['downloadRate'] = (rcvd - self.data['inBytes']) / (now - self.timestamp)
			self.data['downloadRate'] = self.data['downloadRate'] * 8 / 1024 #conver bytes per second to kilo bits per second
			if self.data['downloadRate'] <= 0:
				del self.data['downloadRate']
			self.data['uploadRate'] = (sent - self.data['outBytes']) / (now - self.timestamp)
			self.data['uploadRate'] = self.data['uploadRate'] * 8 / 1024 #conver bytes per second to kilo bits per second
			if self.data['uploadRate'] <= 0:
				del self.data['uploadRate']
			self.data['inBytes'] = rcvd
			self.data['outBytes'] = sent
			self.timestamp = now
			print 'IGD:	', json.dumps(self.data)
			self.dataSink.updateCOSM(self.data, self.conf['igd']['feed_id'])
		except Exception, e:
			print "Error getting IGD Stats: ", e

class UPnPClient(DatagramProtocol):
	def __init__(self, *args, **kwargs):
		self.ConnectionService = 'urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1'
		self.endpoint = None
		reactor.listenUDP(0, self)

	def startProtocol(self):
		self.transport.write('M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: ssdp:discover\r\nMX: 10\r\nST: ssdp:all', ('239.255.255.250', 1900))

	def _cbServiceInfo(self, xml):
		upnp_namespace = 'urn:schemas-upnp-org:device-1-0'
		root = ET.fromstring(xml)
		urlbase = root.find(str(QName(upnp_namespace,'URLBase'))).text
		for child in root.findall('.//'+str(QName(upnp_namespace,'service'))):
			if child.find(str(QName(upnp_namespace,'serviceType'))).text == self.ConnectionService:
				endpoint = urlbase + child.find(str(QName(upnp_namespace,'controlURL'))).text
				server = SOAPProxy(endpoint, self.ConnectionService)
				soapaction = self.ConnectionService+"#GetCommonLinkProperties"
				if server._sa(soapaction).GetCommonLinkProperties()['NewPhysicalLinkStatus'] == 'Up':
					self.endpoint = endpoint

	def _cbError(self, msg):
		print msg

	def GetTotalBytesReceived(self):
		server = SOAPProxy(self.endpoint, self.ConnectionService)
		soapaction = self.ConnectionService+"#GetTotalBytesReceived"
		return long(server._sa(soapaction).GetTotalBytesReceived())

	def GetTotalBytesSent(self):
		server = SOAPProxy(self.endpoint, self.ConnectionService)
		soapaction = self.ConnectionService+"#GetTotalBytesSent"
		return long(server._sa(soapaction).GetTotalBytesSent())

	def datagramReceived(self, datagram, address):
		IGDdevice = 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'
		headers = dict(re.findall(r"(?P<name>.*?):(?P<value>.*?)\r\n", datagram))
		if headers['ST'] != IGDdevice:
			return
		getPage(headers['LOCATION']).addCallbacks( callback=self._cbServiceInfo, errback=self._cbError)


if __name__ == "__main__":
	upnp = UPnPClient()
	reactor.run()


