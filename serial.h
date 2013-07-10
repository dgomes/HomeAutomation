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

void parseWeatherJSON(char *json, struct weatherData *data);
int setupSerial(char *port, char *speed);
int readSerial(char *str);
