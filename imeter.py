from datetime import datetime
import calendar
import json
import urllib2
import re

from BeautifulSoup import BeautifulSoup
from twisted.internet import task
from twisted.web import resource

class IMeterCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self, sink, conf):
		self.timestamp = 0
		self.data = {'energy':0, 'power':0, 'energySpent':0}
		self.dataSink = sink
		self.conf = conf
		l = task.LoopingCall(self.cronJob)
		l.start(float(conf['imeter']['pool_interval']))

	def render_GET(self, request):
		data = json.dumps(self.data)
		return jsonpCallback(request, data)

	def cronJob(self):
		try:
			response = urllib2.urlopen(self.conf['imeter']['url'], timeout=10)
			html = response.read()
			soup = BeautifulSoup(html)
			#this is fine tuned :)
			scrap = str(soup.findAll('td')[15])
			non_decimal = re.compile(r'[^\d\n.]+')
			scrap = non_decimal.sub('', scrap)
			data = scrap.split('\n')

			if self.data['energy'] != 0:
				self.data['energySpent'] = int(data[1]) - self.data['energy']
			self.data['energy'] = int(data[1])
			self.data['power'] = int(data[2])
			print self.data
			self.dataSink.updateCOSM(self.data, self.conf['imeter']['feed_id'])
		except Exception as e:
			print e

