#ifndef _CONFIG_H_
#define _CONFIG_H_

#include <jansson.h>
#include "utils.h"

struct config {
	struct _port {
		char *name;
		int speed;
		int timeout; // mili seconds
	} port;
	struct _xively {
		char *key;
		long feedid;	
		int updaterate; //seconds	
	} xively;
	int interval;
};

int readConfig(const char *filename, struct config *c);

#endif
