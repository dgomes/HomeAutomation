#!/usr/bin/python
import yaml
from datetime import datetime
import calendar
import home
from extensions import snmp
from twisted.python import failure
from twisted.internet import reactor

class AirportResource(home.Resource):
	def __init__(self, sink, conf):
		self.conf = conf['airport']
		self.data = {'downloadRate':0, 'inOctets':0, 'uploadRate':0, 'outOctets':0, 'numberWirelessClients':0}
		self.proxy = snmp.AgentProxy(ip=self.conf['ip'], community=self.conf['community'], version=2)
		#create dictionary from conf with mapping between oid and label
		self.mapping = dict()
		for i in [{l['oid']: l['label']} for l in self.conf['items']]:
			self.mapping.update(i)
		#extract oids from conf
		self.oids = [ item['oid'] for item in self.conf['items']]
		self.timestamp = 0
		home.Resource.__init__(self, sink)

	def _cbSuccess(self, results):
		now = calendar.timegm(datetime.utcnow().utctimetuple())
		for res in results.keys():
			if self.mapping[res] == 'inOctets':
				self.data['downloadRate'] = (results[res] - self.data['inOctets']) / (now - self.timestamp)
				self.data['downloadRate'] = self.data['downloadRate'] * 8 / 1024 #convert bytes per second to kilo bits per second
				if self.data['downloadRate'] <= 0:
					del self.data['downloadRate']
			if self.mapping[res] == 'outOctets':
				self.data['uploadRate'] = (results[res] - self.data['outOctets']) / (now - self.timestamp)
				self.data['uploadRate'] = self.data['uploadRate'] * 8 / 1024 #convert bytes per second to kilo bits per second
				if self.data['uploadRate'] <= 0:
					del self.data['uploadRate']
			self.data[self.mapping[res]] = results[res]
		print "Airport:	", self.data
		if self.timestamp != 0:	#discard first results
			self.dataSink.update(self.data, self.conf['feed_id'])
		self.timestamp = now

	def _cbError(self, msg):
		print msg

	def cronJob(self):
		d = self.proxy.get(self.oids)
		d.addCallbacks( callback=self._cbSuccess, errback=self._cbError)

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	airport = AirportResource(None, conf)
	airport.cronJob()
	reactor.run()
