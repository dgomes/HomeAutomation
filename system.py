#!/usr/bin/python
import psutil
import json
from twisted.python import failure
from twisted.internet import reactor
from twisted.web import resource

class SystemResource(resource.Resource):
	isLeaf = True
	def __init__(self):
		self.data = {'cpuUsage':0, 'memTotal':0, 'memUsed':0, 'memAvailable':0, 'disk':{}}

	def render_GET(self,request):
		self.data['cpuUsage'] = psutil.cpu_percent(interval=1)
		self.data['memTotal'] = psutil.virtual_memory().total
		self.data['memUsed'] = psutil.virtual_memory().used
		self.data['memAvailable'] = psutil.virtual_memory().available
		for part in psutil.disk_partitions():
			self.data['disk'][part.mountpoint] = {}
			self.data['disk'][part.mountpoint]['total'] = psutil.disk_usage(part.mountpoint).total
			self.data['disk'][part.mountpoint]['used'] = psutil.disk_usage(part.mountpoint).used

		data = json.dumps(self.data)
		return data

if __name__ == "__main__":
	conf = yaml.load(file('settings.yaml', 'r'))
	system = SystemResource(None, conf)
	reactor.run()
