import sys
import logging
from twisted.protocols.basic import LineOnlyReceiver

class USBClient(LineOnlyReceiver):
	def __init__(self, callback):
		self.callback = callback
	def connectionFailed(self):
		log.err("Connection Failed:", self)
		reactor.stop()

	def lineReceived(self, line):
		logging.debug( "RCV: %s" % repr(line))
		self.callback(line)

	def sendLine(self, cmd):
		logging.debug( "SEND: %s" % cmd)
		self.transport.write(cmd + "\r\n")

	def outReceived(self, data):
		logging.debug("outReceived! with %d bytes!" % len(data))
		self.data = self.data + data

