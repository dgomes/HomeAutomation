#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arduino-serial-lib.h>
#include <time.h>

#define DEBUG
#include "update.h"
#include "json.h"
#include "utils.h"

int setupSerial(char *port, int baudrate) {
	int fd = -1;

	fd = serialport_init(port, baudrate);
	if( fd==-1 ) {
		fprintf(stderr,"couldn't open port %s @ %d bauds\n", port, baudrate);
		return -1;
	}
	debug_print("opened port %s\n",port);

	serialport_flush(fd);
	return fd;
};

int readSerial(int fd, char *buf, int buf_max, int timeout) {
	char eolchar = '\n';

	memset(buf,0,buf_max);  
	int sr = serialport_read_until(fd, buf, eolchar, buf_max, timeout);
	//	strcpy(buf,"{\"code\": 100, \"Humidity\": 47, \"OutdoorTemperature\": 28.40, \"IndoorTemperature\": 27.00}\n");
	debug_print("DEBUG:%d\t%s", sr, buf);

	return sr;
};

int main( int argc, const char* argv[] ) {
	int fd = setupSerial("/dev/ttyUSB0", 115200);

	if(fd == -1)
		exit(1);

	const int buf_max = 512;
	char buf[buf_max];
	char prev[buf_max];

	while(!readSerial(fd, buf, buf_max, 50000)) {
		if(checkJSON_integer(buf,"code", 100)==0) {
			if(strcmp(buf, prev) == 0) {
				printf("%s\n",	updateFeed("HQHeHauTb9jvkpLcepV2Sg5G9SlQkxKOzg8akO9X6r5bC7mW", 1435962501, buf)? "Error updating feed" : "update successfull");
			}
			strcpy(prev, buf);
		}
		serialport_flush(fd);
	};
	fprintf(stderr, "Could not read from serial\n");
	return 0;
}
