#ifndef _SERIAL_H_
#define _SERIAL_H_

#include <arduino-serial-lib.h>

//#define DEBUG

#include "utils.h"
#include "update.h"

int setupSerial(char *port, char *speed);
int readSerial(int fd, char *buf, int buf_max, int timeout)

#endif
