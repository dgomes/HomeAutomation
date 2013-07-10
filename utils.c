#include "utils.h"

int parseWeatherJSON(char *text, struct weatherData *data) {
	if(!strlen(text)) return -1;
	printf(">%s<\n", text);
	
	json_t *root;
	json_error_t error;

	root = json_loads(text, 0, &error);

	if(!root)
	{
		fprintf(stderr, "error: on line %d: %s\n", error.line, error.text);
		return 1;
	}

	json_t *code = json_object_get(root, "code");
	if(!json_is_integer(code))
    {
        fprintf(stderr, "error: code is not a string\n");
        return 1;
    }

	if(json_integer_value(code) != 100)
		return 2;
	else
		data->code = 100;


	json_t *humidity = json_object_get(root, "humidity");
	if(json_is_integer(humidity))
		data->humidity = json_integer_value(humidity);

	json_t *indoor = json_object_get(root, "IndoorTemperature");
	if(json_is_real(indoor))
		data->indoor = json_real_value(indoor);

	json_t *outdoor = json_object_get(root, "OutdoorTemperature");
	if(json_is_real(outdoor))
		data->outdoor = json_real_value(outdoor);


	return 0;
}
