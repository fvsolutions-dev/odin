#include <stdint.h>
#include <stdbool.h>
#include "odin.h"

int ODIN_element_to_string(ODIN_element_type_t element_type, void *data, char *buffer, uint8_t size);

int ODIN_encode_to_string(const ODIN_parameter_t *parameter, char *output_buffer, uint8_t size, uint16_t access_group);
