from datetime import datetime
import calendar
import json
import urllib2
import re

from BeautifulSoup import BeautifulSoup
from twisted.internet import task
from twisted.web import resource
from twisted.web.client import getPage

class IMeterCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self, sink, conf):
		self.timestamp = 0
		self.data = {'energy':0, 'power':0, 'energySpent':0}
		self.dataSink = sink
		self.conf = conf
		l = task.LoopingCall(self.cronJob)
		l.start(float(self.conf['imeter']['pool_interval']))

	def render_GET(self, request):
		data = json.dumps(self.data)
		return jsonpCallback(request, data)

	def cronJob(self):
		getPage(self.conf['imeter']['url']).addCallbacks(callback=self._cb_success, errback=self._cb_error)

	def _cb_error(self, msg):
		print "Error getting page from imeter"

	def _cb_success(self, html):
		try:
			soup = BeautifulSoup(html)
			#this is fine tuned :)
			scrap = str(soup.findAll('td')[15])
			non_decimal = re.compile(r'[^\d\n.]+')
			scrap = non_decimal.sub('', scrap)
			data = scrap.split('\n')
			if self.data['energy'] != 0:
				self.data['energySpent'] = (int(data[1]) - self.data['energy'])
			else:
				del self.data['energySpent']
			self.data['energy'] = int(data[1])
			self.data['power'] = int(data[2])
			print 'iMeter:	', self.data


			#TODO check if Last Recption changed ...
			self.dataSink.updateCOSM(self.data, self.conf['imeter']['feed_id'])
		except Exception as e:
			log.err(e)

