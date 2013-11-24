HomeAutomation
==============

As the name implies this is a personal Home Automation Project, currently living out of a IR+RF Remote Controler and a Weather Station.

Configuration
=============

In order to execute the daemon you require a configuration file in JSON format 

Example contents of settings.yaml:

<pre>
{
"port": {
	"name": "/dev/ttyUSB0",
	"speed": 115200,
	"timeout": 20000
	},
"xively": {
	"key": "wecjeorijc3oircjoerijvoirjveoirjvroisjvoe",
	"feedid": 123456789,
	"updaterate": 5 
	}
}
</pre>
