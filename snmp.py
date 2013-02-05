#!/usr/bin/python
import yaml

import home
from extensions import snmp
from twisted.python import failure
from twisted.internet import reactor

oids = ['.1.3.6.1.4.1.63.501.3.2.1.0',
		'.1.3.6.1.2.1.2.2.1.10.6',
		'.1.3.6.1.2.1.2.2.1.16.6']

class SNMPResource(home.Resource):
	def __init__(self, sink, conf):
		self.conf = conf['airport']
		self.data = {'downloadRate':0, 'inOctets':0, 'uploadRate':0, 'outOctets':0, 'numberWirelessClients':0}
		self.proxy = snmp.AgentProxy(ip='192.168.1.72', community='public', version=2)
		home.Resource.__init__(self, sink)

	def _cbSuccess(self, results):
		print "success"
		print results

	def _cbError(self, msg):
		print msg

	def cronJob(self):
		print "CronJob"
		d = self.proxy.get(oids)
		d.addCallbacks( callback=self._cbSuccess, errback=self._cbError)

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	airport = SNMPResource(None, conf)
	airport.cronJob()
	reactor.run()
