#include "odin.h"

int ODIN_parameter_read(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
int ODIN_parameter_read_into_buffer(const ODIN_parameter_t *parameter, void *output_buffer, size_t output_buffer_size,
                                    uint16_t access_group);
int ODIN_get_data_size(const ODIN_parameter_t *parameter);
