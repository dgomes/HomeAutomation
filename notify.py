#!/usr/bin/python
import cgi
import yaml
import pprint
import json
import twitter
from twisted.web.error import ForbiddenResource
from twisted.python import failure
from twisted.internet import reactor
from twisted.web import resource
from twisted.web import server, static

class NotifyResource(resource.Resource):
	isLeaf = True
	def __init__(self, conf):
		self.conf = conf['notify']
		self.api = twitter.Api(consumer_key=conf['notify']['consumer_key'],
		                      consumer_secret=conf['notify']['consumer_secret'],
							  access_token_key=conf['notify']['access_token_key'],
							  access_token_secret=conf['notify']['access_token_secret'])

	def render_POST(self,request):
		#pprint.pprint(request.__dict__)
		if [tok for tok in request.postpath if tok in [ auth['token'] for auth in self.conf['auth']]]:
			if 'cosm' in request.postpath:
				data = json.loads(request.args['body'][0])
				message = "COSM: '" + unicode(data['environment']['title']) + "' was triggered due to value " + unicode(data['triggering_datastream']['value']['value']) + unicode(data['triggering_datastream']['units']['symbol'])+" " + unicode(data['type']) + " " + unicode(data['threshold_value']) + unicode(data['triggering_datastream']['units']['symbol'])
			else:
				message = cgi.escape(request.postpath[-1])
			try:
				self.api.PostDirectMessage(self.conf['twitter_id'], message)
				print "sent direct message to "+self.conf['twitter_id']
			except twitter.TwitterError, e:
				print e
				return message + " " + e
			return message
		page = ForbiddenResource(message="You are not authorized!")
		return page.render(request)

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	notify = NotifyResource(conf['notify'])
	reactor.listenTCP(8000, server.Site(notify))
	reactor.run()
