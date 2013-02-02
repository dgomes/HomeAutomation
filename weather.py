from datetime import datetime
import calendar
import json

from twisted.web import server, resource, static

class WeatherCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self, sink, conf):
		self.timestamp = 0
		self.data = {'humidity':0, 'indoor_temp':0, 'outdoor_temp':0}
		self.dataSink = sink
	def render_GET(self, request):
		data = json.dumps({"humidity": self.data['humidity'], "indoor_temp": self.data['indoor_temp'], "outdoor_temp": self.data['outdoor_temp'] })
		return jsonpCallback(request, data)

	def updateData(self, line):
		try:
			d = json.loads(line)
			if d[u'code'] != 100:  #we only care for weather station reports (code 100)
				return
		except:
			return

		# make sure we are in the same sample acquisition window, else we start from 0
		if calendar.timegm(datetime.utcnow().utctimetuple()) - self.timestamp < 5:
			if self.data['humidity'] == d[u'Humidity'] and self.data['indoor_temp'] ==  d[u'IndoorTemperature'] and self.data['outdoor_temp'] == d[u'OutdoorTemperature']:
				self.samples+=1
			else:
				self.samples-=1
		else:
			self.samples = 0

		# we don't have enough samples so we take a new measure
		if self.samples < 1:
			self.data['humidity'] = d[u'Humidity']
			self.data['indoor_temp'] =  d[u'IndoorTemperature']
			self.data['outdoor_temp'] = d[u'OutdoorTemperature']
			self.samples+=1
		self.timestamp = calendar.timegm(datetime.utcnow().utctimetuple())

		# 3 consistent samples? lets publish this stuff!
		if self.samples == conf['min_samples']:
			sink.updateCOSM(self.data)
			self.samples = 0
