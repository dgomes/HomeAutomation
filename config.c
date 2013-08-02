#include "config.h"

int readConfig(const char *filename, struct config *c) {
        if(!strlen(filename)) return -1;

        json_error_t error;
	json_t *root = json_load_file(filename, 0, &error);

        if(!root) {
                fprintf(stderr, "error: on line %d: %s\n", error.line, error.text);
                return 1;
        }

	/* Port Configuration */
        json_t *port = json_object_get(root, "port");
        if(!json_is_object(port)) {
                fprintf(stderr, "error: port is not an object\n");
                return 1;
        }

	json_t *name = json_object_get(port, "name");
	if(!json_is_string(name)) {
		fprintf(stderr, "error: port name missing\n");
		return 1;
	}
	c->port.name = malloc(strlen(json_string_value(name)));
	strcpy(c->port.name,json_string_value(name));	
	json_t *speed = json_object_get(port, "speed");
	if(!json_is_integer(speed)) {
		fprintf(stderr, "error: port speed missing\n");
		return 1;
	}
	c->port.speed = json_integer_value(speed);	
	json_t *timeout = json_object_get(port, "timeout");
	if(!json_is_integer(timeout)) {
		fprintf(stderr, "error: port timeout missing\n");
		return 1;
	}
	c->port.timeout = json_integer_value(timeout);	

	/* Xively Configuration */
	json_t *xively = json_object_get(root, "xively");
        if(!json_is_object(xively)) {
                fprintf(stderr, "error: xively is not an object\n");
                return 1;
        }
	json_t *key = json_object_get(xively, "key");
        if(!json_is_string(key)) {
                fprintf(stderr, "error: xively key missing\n");
                return 1;
        }
        c->xively.key = malloc(strlen(json_string_value(key)));
        strcpy(c->xively.key,json_string_value(key));
        json_t *feed = json_object_get(xively, "feedid");
        if(!json_is_integer(feed)) {
                fprintf(stderr, "error: xively feedId missing\n");
                return 1;
        }
        c->xively.feedid = json_integer_value(feed);

        return 0;
}
