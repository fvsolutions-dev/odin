#include <stdint.h>
#include <stdbool.h>
#include "odin.h"

int ODIN_element_to_string(ODIN_element_type_t element_type, void *data, char *output_buffer, size_t output_buffer_size);
int ODIN_encode_to_string(const ODIN_parameter_t *parameter, char *output_buffer, size_t output_buffer_size, uint16_t access_group);
