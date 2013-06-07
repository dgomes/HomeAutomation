import xively
import datetime
import sys
import time

class XivelyInterface():
	def __init__(self, conf):
		self.api = xively.XivelyAPIClient(conf['xively']['ApiKey'])

	def update(self, data, feedId):
		feed = self.api.feeds.get(feedId)
		now = datetime.datetime.now()
		stream = []
		for i in data.keys():
			stream.append(xively.Datastream(id=i, current_value=data[i]))

		feed.datastreams = stream 
		# Update the Xively service with latest value(s)
		feed.update()
		print "Successfully published to Xively"

