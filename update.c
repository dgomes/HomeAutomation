#include "update.h"

int updateFeed(char *ApiKey, int feed_id, struct weatherData *data) {
	if(data->code != 100) return -1;
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
	f.datastream_count  = 3;

	xi_datapoint_t datapoint;
	{ // get actual timestamp
		time_t timer = 0;
		time( &timer );
		datapoint.timestamp.timestamp = timer;
	}


	xi_datastream_t* d = &f.datastreams[0];
	d->datapoint_count   = 1;
	xi_str_copy_untiln(d->datastream_id, sizeof( d->datastream_id ), "humidity", '\0');
	xi_datapoint_t* p = &d->datapoints[0];
	xi_set_value_i32( p, data->humidity);

	d = &f.datastreams[1];
	d->datapoint_count   = 1;
	xi_str_copy_untiln(d->datastream_id, sizeof( d->datastream_id ), "indoor_temp", '\0');
	p = &d->datapoints[0];
	xi_set_value_f32( p, data->indoor);

	d = &f.datastreams[2];
	d->datapoint_count   = 1;
	xi_str_copy_untiln(d->datastream_id, sizeof( d->datastream_id ), "outdoor_temp", '\0');
	p = &d->datapoints[0];
	xi_set_value_f32( p, data->outdoor);


	xi_feed_update( xi_context, &f );

	printf( "err: %d - %s\n", ( int ) xi_get_last_error(), xi_get_error_string( xi_get_last_error() ) );

	// destroy the context cause we don't need it anymore
	xi_delete_context( xi_context );

	return 0;
}
