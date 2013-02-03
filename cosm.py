import txcosm
from txcosm.HTTPClient import HTTPClient

class CosmInterface():
	def __init__(self, conf):
		self.conf = conf

	def successlog(self, msg):
		print "Successfully published to COSM"

	def errorlog(self, msg):
		print "Error publishing: ", msg

	def updateCOSM(self, data, feed):
		cosmClient = HTTPClient(api_key=self.conf['cosm']['ApiKey'], feed_id=feed)
		environment = txcosm.Environment(version="1.0.0")
		for i in data.keys():
			environment.setCurrentValue(i, data[i])

		# Update the Cosm service with latest value(s)
		d = cosmClient.update_feed(data=environment.encode())
		d.addCallback(self.successlog)
		d.addErrback(self.errorlog)

