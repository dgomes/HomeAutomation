#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arduino-serial-lib.h>
#include <time.h>

#define DEBUG
#include "update.h"
#include "json.h"
#include "utils.h"
#include "config.h"

int setupSerial(char *port, int baudrate) {
	int fd = -1;

	fd = serialport_init(port, baudrate);
	if( fd==-1 ) {
		fprintf(stderr,"couldn't open port %s @ %d bauds\n", port, baudrate);
		return -1;
	}
	debug_print("opened port %s @ %d bps\n",port, baudrate);

	serialport_flush(fd);
	return fd;
};

int readSerial(int fd, char *buf, int buf_max, int timeout) {
	char eolchar = '\n';

	memset(buf,0,buf_max);  
	int sr = serialport_read_until(fd, buf, eolchar, buf_max, timeout);
	debug_print("DEBUG:%d\t%s", sr, buf);

	return sr;
};

int main( int argc, const char* argv[] ) {
	struct config cfg;
	
	char conf[strlen(argv[0] + 10)];
	strcat(strcpy(conf,argv[0]), ".json");
	if(readConfig(conf, &cfg)) {
		//can't find configuration file in current dir, lookup in /etc/
		strcat(strcat(strcpy(conf, "/etc/"), argv[0]), ".json");
		fprintf(stderr,"Reading configuration from %s\n", conf);
		if(readConfig(conf,&cfg)) 
			// no configuration file supplied
			exit(1);	
	}

	int fd = setupSerial(cfg.port.name, cfg.port.speed);

	if(fd == -1)
		exit(2);

	const int buf_max = 512;
	char buf[buf_max];
	char last[buf_max];
	time_t lasttime = time(NULL);
	time_t updatetime = 0;

	while(!readSerial(fd, buf, buf_max, cfg.port.timeout)) {
		fprintf(stderr, "%s\n", buf);
		if(checkJSON_integer(buf,"code", 200)==0) {
			lasttime = time(NULL);
			strcpy(last, buf);
		}
		if((lasttime - updatetime > cfg.xively.updaterate) && strlen(last)>0) {
			if(updateFeed(cfg.xively.key, cfg.xively.feedid, last)) {
				printf("FAILED updated\n");
			} else {
				printf("updated\n");
				updatetime = time(NULL);
				strcpy(last,"");
			};
		}
		serialport_flush(fd);
	};
	fprintf(stderr, "Could not read from serial\n");
	return 0;
}
