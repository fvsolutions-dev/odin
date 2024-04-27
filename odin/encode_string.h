#include <stdint.h>
#include <stdbool.h>
#include "odin_datastore.h"

int ODIN_read_as_string(ODIN_parameter_t *parameter, char *buffer, uint8_t size, uint16_t access_group);
int ODIN_write_to_string(ODIN_parameter_t *parameter, char *input, uint16_t access_group);
