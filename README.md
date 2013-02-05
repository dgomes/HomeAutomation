Dependencies
============

https://raw.github.com/vincentbernat/wiremaps/master/wiremaps/collector/snmp.c

HomeAutomation
==============

As the name implies this is a personal Home Automation Project, currently living out of a IR+RF Remote Controler and a Weather Station.

Configuration
=============

In order to execute the daemon you require a configuration file named settings.yaml.

Example contents of settings.yaml:

<pre>
logfile: sys.stdout
port: 8888
serial:
 port: /dev/tty.usbmodemfd111
 baudrate: 115200
igd:
 feed_id: 11111
 pool_interval: 30
imeter:
 url: "http://imeter.local./listdev.htm"
 feed_id: 22222
 pool_interval: 300
weather:
 feed_id: 33333
airport:
 pool_interval: 100
cosm:
 ApiKey: fwoifjedovheovjeOHFRUHojRORhUOORFOORFHRFO
</pre>
