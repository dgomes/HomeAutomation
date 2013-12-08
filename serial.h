#ifndef _SERIAL_H_
#define _SERIAL_H_

#include <arduino-serial-lib.h>

//#define DEBUG

#include "utils.h"
#include "update.h"

#define BUF_MAX  512
int setupSerial(char *port, int baudrate);
int readSerial(int fd, char *buf, int buf_max, int timeout);

struct last_update {
	char *buf;
	time_t time;
};
#endif
