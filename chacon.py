import utils
import httplib
from os import path
from twisted.web import resource

class Chacon:
	codes = {'A1': {'on': 'R000280B7', 'off': 'R000280B8'},
			 'A2': {'on': 'R0002A2E3', 'off': 'R0002A2E2'},
			 'A3': {'on': 'R0002AE47', 'off': 'R0002AE46'},
			 'A4': {'on': 'R0002B213', 'off': 'R0002A2E2'},
			 'B1': {'on': 'R00061B5B', 'off': 'R0002B212'},
			 'B2': {'on': 'R00063D87', 'off': 'R00061B5A'},
			 'B3': {'on': 'R000648EB', 'off': 'R00063D86'},
			 'B4': {'on': 'R00064CB7', 'off': 'R00064CB6'},
			 'C1': {'on': 'R00074EE7', 'off': 'R00074EE6'},
			 'C2': {'on': 'R00077113', 'off': 'R00077112'},
			 'C3': {'on': 'R00077C77', 'off': 'R00077C76'},
			 'C4': {'on': 'R00078043', 'off': 'R00078042'},
	 }

class RFCommandResource(resource.Resource):
	isLeaf = True
	def __init__(self, serial):
		self.serial = serial

	def render_GET(self, request):
		command = request.path.split('/')
		try:
			cmd = Chacon.codes[command[2]][command[3]]
			self.serial.writeSomeData(cmd)
		except:
			log.err()
			return jsonpCallback(request, "{ 'result': 400 }")
		return jsonpCallback(request, "{ 'result': 200 }")
