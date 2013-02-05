import json
import urllib2
import re

import home

from BeautifulSoup import BeautifulSoup
from twisted.web.client import getPage

class IMeterResource(home.Resource):
	def __init__(self, sink, conf):
		self.conf = conf['imeter']
		self.data = {'energy':0, 'power':0, 'energySpent':0}
		home.Resource.__init__(self, sink)

	def cronJob(self):
		getPage(self.conf['url']).addCallbacks(callback=self._cb_success, errback=self._cb_error)

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
			self.dataSink.updateCOSM(self.data, self.conf['feed_id'])
		except Exception as e:
			log.err(e)

