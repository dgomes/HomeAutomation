#ifndef _DATA_H_
#define _DATA_H_
// {"code": 100, "Humidity": 47, "OutdoorTemperature": 28.40, "IndoorTemperature": 27.00}
struct weatherData {
	char code;
	int humidity;
	double outdoor;
	double indoor;
};

#endif
