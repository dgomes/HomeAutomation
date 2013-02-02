import httplib
from twisted.web import resource
from os import path

class Sony:
	codes = {'power': 'S00000a90',
		 '1': 'S00000010',
		 '2': 'S00000810',
		 '3': 'S00000410',
		 '4': 'S00000c10',
		 '5': 'S00000210',
		 '6': 'S00000a10',
		 '7': 'S00000610',
		 '8': 'S00000e10',
		 '9': 'S00000110',
		 '0': 'S00000010',
		 'source': 'S000002f0',
		 'AV': 'S00000a50',
		 'volup': 'S00000490',
		 'Pup': 'S00000090',
		 'voldown': 'S00000c90',
		 'Pdown': 'S00000890',
	}

class IRCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self, serial):
		self.serial = serial

	def jsonpCallback(request, data):
		callback = request.args.get('callback')

		if callback:
			callback = callback[0]
			data = '%s(%s);' % (callback, data)
			return data
		return "callback({'error': 'no callback defined'})"

	def render_GET(self, request):
		command = request.path.split('/')
		print command
		try:
			cmd = Sony.codes[command[2]]
			self.serial.writeSomeData(cmd)
		except:
			log.err()
			return jsonpCallback(request, "{ 'result': 400 }")
		return jsonpCallback(request, "{ 'result': 200 }")

