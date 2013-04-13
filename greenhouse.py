import json
import urllib2
import re
import yaml
import home
from twisted.python import log
from twisted.python import failure
from twisted.internet import reactor
from twisted.web import resource
from twisted.web.client import getPage

class GreenHouseResource(home.Resource):
	def __init__(self, sink, conf):
		self.conf = conf['greenhouse']
		self.data = {'Humidity': 0, 'Temperature': 0, 'Luminosity': 0, 'Water': 0 }
		home.Resource.__init__(self, sink)

	def cronJob(self):
		response = urllib2.urlopen(self.conf['url'], timeout=5)
		self.data = json.loads(response.read())
		#getPage(self.conf['url']).addCallbacks(callback=self._cb_success, errback=self._cb_error)
		del self.data['HumidityProbe']
		print self.data
		self.dataSink.updateCOSM(self.data, self.conf['feed_id'])

	def _cb_error(self, msg):
		print "Error getting page from imeter"

	def _cb_success(self, html):
		print html
		try:
			#TODO check if Last Recption changed ...
			self.dataSink.updateCOSM(self.data, self.conf['feed_id'])
		except Exception as e:
			log.err(e)

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	gh = GreenHouseResource(None, conf)
	reactor.run()
