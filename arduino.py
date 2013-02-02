from twisted.protocols.basic import LineOnlyReceiver

class USBClient(LineOnlyReceiver):
	def __init__(self, callback):
		self.callback = callback

	def connectionFailed(self):
		log.err("Connection Failed:", self)
		reactor.stop()

	def lineReceived(self, line):
		print >> sys.stderr, "RCV: ", repr(line)
		self.callback(line)

	def sendLine(self, cmd):
		print >> sys.stderr, "SEND: ", cmd
		self.transport.write(cmd + "\r\n")

	def outReceived(self, data):
		print >> sys.stderr, ("outReceived! with %d bytes!" % len(data))
		self.data = self.data + data

