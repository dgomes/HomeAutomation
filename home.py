import json
from twisted.internet import task
from twisted.web import resource
from twisted.internet import reactor

class Resource(resource.Resource):
	isLeaf = True
	def __init__(self, sink):
		if not hasattr(self, 'data'):
			self.data = None
		if not hasattr(self, 'conf'):
			self.conf = None
		self.dataSink = sink
		if 'pool_interval' in self.conf:
			l = task.LoopingCall(self.cronJob)
			l.start(float(self.conf['pool_interval']))

	@staticmethod
	def _jsonpCallback(request, data):
		callback = request.args.get('callback')

		if callback:
			callback = callback[0]
			data = '%s(%s);' % (callback, data)
			return data
		return "callback({'error': 'no callback defined'})"

	def render_GET(self, request):
		data = json.dumps(self.data)
		return self._jsonpCallback(request, data)

	def cronJob(self):
		raise NotImplementedError("Subclasses should implement this!")

