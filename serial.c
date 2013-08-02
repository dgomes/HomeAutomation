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
		strcat(strcat(strcpy(conf, "/etc/"), argv[0]), ".json");
		fprintf("Reading configuration from %s\n", conf);:w
		if(readConfig(conf,&cfg)) 
			exit(1);	
	}

	int fd = setupSerial(cfg.port.name, cfg.port.speed);

	if(fd == -1)
		exit(2);

	const int buf_max = 512;
	char buf[buf_max];
	char prev[buf_max];

	while(!readSerial(fd, buf, buf_max, cfg.port.timeout)) {
		if(checkJSON_integer(buf,"code", 100)==0) {
			if(strcmp(buf, prev) == 0) {
				printf("%s\n",	updateFeed(cfg.xively.key, cfg.xively.feedid, buf)? "Error updating feed" : "update successfull");
			}
			strcpy(prev, buf);
		}
		serialport_flush(fd);
	};
	fprintf(stderr, "Could not read from serial\n");
	return 0;
}
