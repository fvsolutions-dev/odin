
#include "encoding/encode_string.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "inttypes.h"
#include "odin_core.h"

static const char *TAG = "ODIN_STR";

#define ODIN_PRINT_BUFFER_SIZE 128

/**
 * @brief Serialise an element to a human readable string
 *
 * @param element_type Type of the element
 * @param data Pointer to the data
 * @param output_buffer Pointer to the buffer to store the string
 * @param output_buffer_size Size of the buffer
 *
 * @return int Length of the string
 */
int ODIN_element_to_string(ODIN_element_type_t element_type, void *data, char *output_buffer,
                           size_t output_buffer_size) {
    int len = 0;
    switch (element_type) {
        case ODIN_ELEMENT_TYPE_UINT8:
            return snprintf(output_buffer, output_buffer_size, "%" PRIu8, *(uint8_t *)data);

        case ODIN_ELEMENT_TYPE_INT8:
            return snprintf(output_buffer, output_buffer_size, "%" PRId8, *(int8_t *)data);

        case ODIN_ELEMENT_TYPE_UINT16:
            return snprintf(output_buffer, output_buffer_size, "%" PRIu16, *(uint16_t *)data);

        case ODIN_ELEMENT_TYPE_INT16:
            return snprintf(output_buffer, output_buffer_size, "%" PRId16, *(int16_t *)data);

        case ODIN_ELEMENT_TYPE_UINT32:
            return snprintf(output_buffer, output_buffer_size, "%" PRIu32, *(uint32_t *)data);

        case ODIN_ELEMENT_TYPE_INT32:
            return snprintf(output_buffer, output_buffer_size, "%" PRId32, *(int32_t *)data);

        case ODIN_ELEMENT_TYPE_UINT64:
            return snprintf(output_buffer, output_buffer_size, "%" PRIu64, *(uint64_t *)data);

        case ODIN_ELEMENT_TYPE_INT64:
            return snprintf(output_buffer, output_buffer_size, "%" PRId64, *(int64_t *)data);

        case ODIN_ELEMENT_TYPE_BOOL:
            return snprintf(output_buffer, output_buffer_size, "%s", (*(bool *)data) ? "true" : "false");

        case ODIN_ELEMENT_TYPE_FLOAT32:
            return snprintf(output_buffer, output_buffer_size, "%f", *(float *)data);

        case ODIN_ELEMENT_TYPE_FLOAT64:
            return snprintf(output_buffer, output_buffer_size, "%f", *(double *)data);

        case ODIN_ELEMENT_TYPE_HEX:
            return snprintf(output_buffer, output_buffer_size, "0x%02x", *(uint8_t *)data);

        default:
            return ODIN_ERROR_NOT_SUPPORTED;
    }
}

/**
 * @brief Serialise a parameter to a human readable string
 *
 * @param parameter Pointer to the parameter
 * @param output_buffer Pointer to the buffer to store the string
 * @param size Size of the buffer
 * @param access_group Access group to check if the parameter is accessible
 *
 * @return int Length of the string
 */
int ODIN_encode_to_string(const ODIN_parameter_t *parameter, char *output_buffer, size_t output_buffer_size,
                          uint16_t access_group) {
    // TODO: Check if the parameter is accessible

    uint8_t data_buffer[ODIN_PRINT_BUFFER_SIZE];
    int ret_size = ODIN_parameter_read_into_buffer(parameter, data_buffer, sizeof(data_buffer), access_group);
    if (ret_size <= 0) {
        return ret_size;
    }

    switch (parameter->odin_type) {
        case ODIN_TYPE_PARAMETER:
            return ODIN_element_to_string(parameter->element_type, data_buffer, output_buffer, output_buffer_size);

        case ODIN_TYPE_VECTOR:
        case ODIN_TYPE_ARRAY: {
            // Print all elements formatted in square brackets

            int len = 0;
            output_buffer[len++] = '[';
            uint8_t *data_buffer_ptr = data_buffer;

            for (; data_buffer_ptr < data_buffer + ret_size; data_buffer_ptr += parameter->element_size) {
                len += ODIN_element_to_string(parameter->element_type, data_buffer_ptr, output_buffer + len,
                                              output_buffer_size - len);
                // cast fo rdouble
                double *data = (double *)data_buffer_ptr;
                // if not last
                if (data_buffer_ptr < data_buffer + ret_size - parameter->element_size) {
                    output_buffer[len++] = ',';
                    output_buffer[len++] = ' ';
                }

                // if buffer is, nearly full add ... and break
                if (len >= output_buffer_size - 10) {
                    len += snprintf(output_buffer + len, output_buffer_size - len, "...");
                    break;
                }
            }
            output_buffer[len++] = ']';
            output_buffer[len] = '\0';

            return len;
        } break;

        default:
            return ODIN_ERROR_NOT_SUPPORTED;
    }
}
