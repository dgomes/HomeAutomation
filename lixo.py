from extensions import snmp
from twisted.python import failure
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import defer

oids = ['.1.3.6.1.4.1.63.501.3.2.1.0',
        '.1.3.6.1.2.1.2.2.1.10.6',
        '.1.3.6.1.2.1.2.2.1.16.6']

d = defer.Deferred()
proxy = snmp.AgentProxy(ip='192.168.1.72', community='public', version=2)

def printResults(results):
    if reactor.running:
        reactor.stop()
    if isinstance(results, failure.Failure):
        raise results.value
    import pprint
    pprint.pprint(results)
    return results

def cron():
	d = proxy.get(oids).addBoth(printResults)

l = task.LoopingCall(cron)
l.start(5.0)
reactor.run()
