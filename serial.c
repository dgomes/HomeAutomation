#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arduino-serial-lib.h>

//#define DEBUG

#ifdef DEBUG
#define debug_print(fmt, ...) fprintf(stderr, fmt, __VA_ARGS__)
#else
#define debug_print(fmt, ...) do {} while (0)
#endif

#include "update.h"
#include "data.h"

void parseWeatherJSON(char *json, struct weatherData *data) {
	char *code, *humidity, *outdoor, *indoor;
	char *delim = ",";
	code = strtok(json, delim);
	debug_print("%s\n", code+8);
	if(strtol(code+8, NULL, 10) == 100) {
		humidity = strtok(NULL, delim);
		debug_print("%s\n", humidity+13);
		outdoor = strtok(NULL, delim);
		debug_print("%s\n", outdoor+23);
		indoor = strtok(NULL, delim);
		debug_print("%s\n", indoor+22);

		data->code = 100;
		data->humidity = strtol(humidity+13, NULL, 10);
		data->outdoor = strtod(outdoor+23, NULL);
		data->indoor = strtod(indoor+22, NULL);
	}
}

int setupSerial(char *port, int baudrate) {
	int fd = -1;

	fd = serialport_init(port, baudrate);
	if( fd==-1 ) {
		fprintf(stderr,"couldn't open port %s @ %d bauds\n", port, baudrate);
		return -1;
	}
	debug_print("opened port %s\n",serialport);

	serialport_flush(fd);
	return fd;
};

int readSerial(int fd, char *buf, int buf_max, int timeout) {
	char eolchar = '\n';

	memset(buf,0,buf_max);  //
	int sr = serialport_read_until(fd, buf, eolchar, buf_max, timeout);
	//	strcpy(buf,"{\"code\": 100, \"Humidity\": 47, \"OutdoorTemperature\": 28.40, \"IndoorTemperature\": 27.00}\n");
	printf("DEBUG:\t%s", buf);

	return sr;
};

int main( int argc, const char* argv[] ) {

	int fd = setupSerial("/dev/ttyUSB0", 115200);

	if(fd == -1)
		exit(1);

	const int buf_max = 256;
	char buf[buf_max];


	do {
		while(!readSerial(fd, buf, buf_max, 5000)) {
			struct weatherData data;
			parseWeatherJSON(buf, &data);

			printf("-\nHumidity: %d\nOutdoor: %f\nIndoor: %f\n", data.humidity, data.outdoor, data.indoor);

			updateFeed("WmJNDWkbkxD29IMuxsq6rdItKrX4hflgtqR0H23QqwuxhBXG", 1435962501, &data);
		};
		fprintf(stderr, "Could not read from serial\n");
	} while(1);
	return 0;
}
