#include "update.h"
#include "json.h"
#undef XI_DEBUG_OUTPUT
int updateFeed(char *ApiKey, int feed_id, const char* text) {
	if(checkJSON_integer(text, "code", 200))
		return 1;

	json_error_t error;
	json_t *root = json_loads(text, 0, &error);
	// create the xi library context
	xi_context_t* xi_context = xi_create_context( XI_HTTP, ApiKey , feed_id );
	
	// check if everything works
	if( xi_context == 0 ) {
		return -1;
	}


	// create feed
	xi_feed_t f;
	memset( &f, 0, sizeof( xi_feed_t ) );
	// set datastream count
	f.feed_id           = feed_id;
	f.datastream_count  = json_object_size(root);

	xi_datapoint_t datapoint;
	{ // get actual timestamp
		time_t timer = 0;
		time( &timer );
		datapoint.timestamp.timestamp = timer;
	}


	xi_datastream_t* d;
	int i = 0;
	const char *key;
	json_t *value;
	void *iter = json_object_iter(root);
	while(iter) {
		key = json_object_iter_key(iter);
		value = json_object_iter_value(iter);
		/* use key and value ... */
		d = &f.datastreams[i++];
		d->datapoint_count   = 1;
		xi_str_copy_untiln(d->datastream_id, sizeof( d->datastream_id ), key, '\0');
		xi_datapoint_t* p = &d->datapoints[0];
		if(json_is_integer(value))
			xi_set_value_i32( p, json_integer_value(value));
		else if(json_is_real(value))
			xi_set_value_f32( p, json_real_value(value));
/*		else
			return 2;	*/

		iter = json_object_iter_next(root, iter);
	}


	xi_feed_update( xi_context, &f );

	if(( int ) xi_get_last_error() > 0)
		printf( "err: %d - %s\n", ( int ) xi_get_last_error(), xi_get_error_string( xi_get_last_error() ) );

	// destroy the context cause we don't need it anymore
	xi_delete_context( xi_context );

	return 0;
}
