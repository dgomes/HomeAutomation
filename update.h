#ifndef _UPDATE_H_
#define _UPDATE_H_

#include <xively.h>
#include <xi_helpers.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include <jansson.h>
#include "utils.h"

int updateFeed(char *ApiKey, int feed_id, const char *data);

#endif 
