#ifndef _UTILS_H_
#define _UTILS_H_

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#ifdef DEBUG
#define debug_print(fmt, ...) fprintf(stderr, fmt, __VA_ARGS__)
#else
#define debug_print(fmt, ...) do {} while (0)
#endif


#endif
