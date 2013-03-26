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
appname: Home Automation
logdir: /tmp
logfile: sys.stdout
port: 8888
serial:
 port: /dev/tty.usbmodemfd111
 baudrate: 115200
igd:
 feed_id: 66666
 pool_interval: 30
imeter:
 url: "http://192.168.1.100/listdev.htm"
 feed_id: 33333
 pool_interval: 300
weather:
 feed_id: 99999
airport:
 ip: "192.168.1.72"
 community: "public"
 pool_interval: 100
 items:
  - oid: ".1.3.6.1.4.1.63.501.3.2.1.0"
    label: "numberWirelessClients"
  - oid: ".1.3.6.1.2.1.2.2.1.10.4"
    label: "inOctets"
  - oid: ".1.3.6.1.2.1.2.2.1.16.4"
    label: "outOctets"
 feed_id: 44444
notify:
 twitter_id: userhandle
 consumer_key: xoxjxoixjioj3i2o32jo2ji
 consumer_secret: TC5114134ojfojoioijoijSOIDR
 access_token_key: 1211111111-0Bh6h4x9VAxxppOJOIJCROJ121331331k
 access_token_secret: oKJJHUYbhjgyuGUYGYIigiyigYIGigIgiyGIYcOQ
 auth:
    - token: q2wsxdr5tgbas023df864
cosm:
 ApiKey: OIFHVSVDDSJjjhwcurhcwihiHFF23424352454553
</pre>
