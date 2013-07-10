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

int parseWeatherJSON(char *json, struct weatherData *data) {
	if(!strlen(json)) return -1;
	printf(">%s<\n", json);
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
		return 0;
	}
	return 1;
}

int main( int argc, const char* argv[] ) {
	const int buf_max = 256;
	char buf[buf_max];

	int fd = -1;
	char serialport[buf_max];
	int baudrate = 9600;  // default
	char eolchar = '\n';
	int timeout = 60000;


	baudrate = strtol("B115200",NULL,10);

	if( fd!=-1 ) {
		serialport_close(fd);
		debug_print("closed port %s\n",serialport);
	}
	strcpy(serialport,"/dev/ttyUSB0");
	fd = serialport_init(serialport, baudrate);
	if( fd==-1 ) error("couldn't open port");
	debug_print("opened port %s\n",serialport);
	serialport_flush(fd);

	do {
		memset(buf,0,buf_max);  // 
		serialport_read_until(fd, buf, eolchar, buf_max, timeout);
		//	strcpy(buf,"{\"code\": 100, \"Humidity\": 47, \"OutdoorTemperature\": 28.40, \"IndoorTemperature\": 27.00}\n");
		printf("DEBUG:\t%s", buf);

		struct weatherData data;
		if(!parseWeatherJSON(buf, &data)) {
		
			printf("-\nHumidity: %d\nOutdoor: %f\nIndoor: %f\n", data.humidity, data.outdoor, data.indoor);
	
			updateFeed("WmJNDWkbkxD29IMuxsq6rdItKrX4hflgtqR0H23QqwuxhBXG", 1435962501, &data);
		}
	} while(1);

	return 0;
}
