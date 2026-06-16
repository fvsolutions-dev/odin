
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "extensions/extensions.h"
#include "inttypes.h"
#include "odin_codec.h"
#include "odin_core.h"

// static const char *TAG = "ODIN_STR";

#define ODIN_PRINT_BUFFER_SIZE 128

/**
 * @brief Serialise an element to a human readable string
 * Note does not handle the custom string encoding
 *
 * @param element_type Type of the element
 * @param data Pointer to the data
 * @param output_buffer Pointer to the buffer to store the string
 * @param output_buffer_size Size of the buffer
 *
 * @return int Length of the string
 */
int ODIN_element_to_string(const ODIN_parameter_t *parameter, void *data, char *output_buffer, size_t output_buffer_size) {
    switch (parameter->element_type) {
        case ODIN_ELEMENT_TYPE_UINT8:
            return snprintf(output_buffer, output_buffer_size, "%" PRIu16, (uint16_t) * (uint8_t *)data);

        case ODIN_ELEMENT_TYPE_INT8:
            return snprintf(output_buffer, output_buffer_size, "%" PRId16, (int16_t) * (int8_t *)data);

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
            return snprintf(output_buffer, output_buffer_size, "%f", (double)*(float *)data);

        case ODIN_ELEMENT_TYPE_FLOAT64:
            return snprintf(output_buffer, output_buffer_size, "%f", *(double *)data);

        case ODIN_ELEMENT_TYPE_HEX:
            return snprintf(output_buffer, output_buffer_size, "0x%02x", *(uint8_t *)data);

        case ODIN_ELEMENT_TYPE_CHAR:
            return snprintf(output_buffer, output_buffer_size, "%c", *(char *)data);

        case ODIN_ELEMENT_TYPE_CUSTOM: {
            // Check if the parameter has a custom string serialisation extension
            const ODIN_extension_t *extension = find_extension(parameter, ODIN_EXTENSION_TYPE_STRING_CODEC);
            if (extension == NULL) {
                // No string codec for this struct type — the runtime has no
                // field metadata to print it properly, so render a graceful
                // summary of one element instead of failing the whole dump.
                return snprintf(output_buffer, output_buffer_size, "<%u B %s>", parameter->element_size,
                                "struct");
            }

            ODIN_string_serialisation_extension_ops_t *ops = (ODIN_string_serialisation_extension_ops_t *)extension->ops;
            return ops->to_string(parameter, data, parameter->element_size, output_buffer, output_buffer_size);
        }
        default:
            return ODIN_ERROR_NOT_SUPPORTED;
    }
}

/**
 * @brief Append one rendered element to an in-progress "[a, b, ...]" string.
 *
 * snprintf returns the WOULD-HAVE-written length when it truncates, so the
 * old `len += ret` pattern pushed `len` past the buffer for long elements
 * (e.g. custom-struct serialisers emitting ~50 B each); the separator writes
 * that followed then corrupted the caller's stack frame, and
 * `output_buffer_size - len` underflowed to a huge size_t. Seen on target as
 * a task-watchdog wedge while odin-dumping vectors of serialised structs.
 *
 * @return 1 element appended (room left for ", " and the "...]" tail),
 *         0 element did not fit — truncated fragment rewound, caller should
 *           append "..." and stop,
 *        <0 codec error.
 */
static int ODIN_append_element_string(const ODIN_parameter_t *parameter, void *element, char *output_buffer,
                                      size_t output_buffer_size, int *len) {
    int ret = ODIN_element_to_string(parameter, element, output_buffer + *len, output_buffer_size - (size_t)*len);
    if (ret < 0) {
        return ret;
    }
    // Reserve room for a ", " separator after this element plus "...]\0".
    if ((size_t)ret + 7 > output_buffer_size - (size_t)*len) {
        output_buffer[*len] = '\0';  // erase the truncated fragment
        return 0;
    }
    *len += ret;
    return 1;
}

// TODO: Add tests for this function
int ODIN_string_to_element(const ODIN_parameter_t *parameter, const char *input_buffer, void *data, size_t data_size) {
    switch (parameter->element_type) {
        case ODIN_ELEMENT_TYPE_UINT8:
            return sscanf(input_buffer, "%" SCNu8, (uint8_t *)data);

        case ODIN_ELEMENT_TYPE_INT8:
            return sscanf(input_buffer, "%" SCNd8, (int8_t *)data);

        case ODIN_ELEMENT_TYPE_UINT16:
            return sscanf(input_buffer, "%" SCNu16, (uint16_t *)data);

        case ODIN_ELEMENT_TYPE_INT16:
            return sscanf(input_buffer, "%" SCNd16, (int16_t *)data);

        case ODIN_ELEMENT_TYPE_UINT32:
            return sscanf(input_buffer, "%" SCNu32, (uint32_t *)data);

        case ODIN_ELEMENT_TYPE_INT32:
            return sscanf(input_buffer, "%" SCNd32, (int32_t *)data);

        case ODIN_ELEMENT_TYPE_UINT64:
            return sscanf(input_buffer, "%" SCNu64, (uint64_t *)data);

        case ODIN_ELEMENT_TYPE_INT64:
            return sscanf(input_buffer, "%" SCNd64, (int64_t *)data);
        case ODIN_ELEMENT_TYPE_FLOAT32:
            return sscanf(input_buffer, "%f", (float *)data);

        case ODIN_ELEMENT_TYPE_FLOAT64:
            return sscanf(input_buffer, "%lf", (double *)data);

            // TODO: add support to the other types
            //  case ODIN_ELEMENT_TYPE_BOOL: {
            //      bool value;
            //      int ret = sscanf(input_buffer, "%d", &value);
            //      if (ret == 1) {
            //          *(bool *)data = value;
            //          return 1;
            //      }
            //      return ret;
            //  }

            // case ODIN_ELEMENT_TYPE_HEX:
            //     return sscanf(input_buffer, "0x%02x", (uint8_t *)data);

            // case ODIN_ELEMENT_TYPE_CUSTOM: {
            //     // Check if the parameter has a custom string serialisation extension
            //     const ODIN_extension_t *extension = find_extension(parameter, ODIN_EXTENSION_TYPE_STRING_CODEC);
            //     if (extension == NULL) {
            //         return ODIN_ERROR_NOT_SUPPORTED;
            //     }

            //     ODIN_string_serialisation_extension_ops_t *ops = (ODIN_string_serialisation_extension_ops_t *)extension->ops;
            //     return ops->from_string(parameter, input_buffer, data, data_size);
            // }

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
int ODIN_encode_parameter_to_string(const ODIN_parameter_t *parameter, char *output_buffer, size_t output_buffer_size,
                                    odin_access_group_t access_group) {
    // TODO: Check if the parameter is accessible

    if (parameter->odin_type == ODIN_TYPE_PARAMETER) {
        uint8_t data_buffer[ODIN_PRINT_BUFFER_SIZE];
        int ret_size = ODIN_parameter_read_into_buffer(parameter, data_buffer, sizeof(data_buffer), access_group);
        if (ret_size < 0) {
            return ret_size;
        }
        if (ret_size == 0) {
            return snprintf(output_buffer, output_buffer_size, "No data");
        }
        return ODIN_element_to_string(parameter, data_buffer, output_buffer, output_buffer_size);
    }

    if (parameter->odin_type == ODIN_TYPE_VECTOR || parameter->odin_type == ODIN_TYPE_ARRAY) {
        // Total payload size and a pointer to the first element. Read element
        // by element straight from the source so arrays of any length work —
        // the old code copied the whole array into a 128 B scratch buffer and
        // returned "Buffer too small" for anything larger.
        int total_size = ODIN_get_data_size(parameter);
        if (total_size < 0) {
            return total_size;
        }
        if (total_size == 0) {
            return snprintf(output_buffer, output_buffer_size, "No data");
        }

        // The element loops below need room for "[" + "...]\0" even when no
        // element fits at all.
        if (output_buffer_size < 8) {
            return ODIN_ERROR_BUFFER_TOO_SMALL;
        }

        // An io-extension-backed parameter has no plain data pointer to walk;
        // fall back to the bounded buffered read (respects the extension).
        // Such arrays are small mapped values in practice.
        if (find_extension(parameter, ODIN_EXTENSION_TYPE_IO) != NULL ||
            parameter->data == NULL) {
            uint8_t data_buffer[ODIN_PRINT_BUFFER_SIZE];
            int ret_size = ODIN_parameter_read_into_buffer(parameter, data_buffer, sizeof(data_buffer), access_group);
            if (ret_size < 0) {
                return ret_size;
            }
            int len = 0;
            output_buffer[len++] = '[';
            for (int off = 0; off + parameter->element_size <= ret_size; off += parameter->element_size) {
                int ret = ODIN_append_element_string(parameter, data_buffer + off, output_buffer, output_buffer_size, &len);
                if (ret < 0) {
                    return ret;
                }
                if (ret == 0) {
                    len += snprintf(output_buffer + len, output_buffer_size - len, "...");
                    break;
                }
                if (off + 2 * parameter->element_size <= ret_size) {
                    output_buffer[len++] = ',';
                    output_buffer[len++] = ' ';
                }
            }
            output_buffer[len++] = ']';
            output_buffer[len] = '\0';
            return len;
        }

        const uint8_t *src;
        if (parameter->odin_type == ODIN_TYPE_VECTOR) {
            // Vector data lives after the num_elements counter (see
            // ODIN_vector_structure_t). data points there.
            src = ((const ODIN_vector_structure_t *)parameter->data)->data;
        } else {
            src = (const uint8_t *)parameter->data;
        }

        int num_elements = parameter->element_size ? (total_size / parameter->element_size) : 0;

        // In case of a string, print it as a string
        if (parameter->element_type == ODIN_ELEMENT_TYPE_CHAR) {
            int n = total_size;
            if (n >= (int)output_buffer_size - 2) {
                n = (int)output_buffer_size - 3;
            }
            return snprintf(output_buffer, output_buffer_size, "\"%.*s\"", n, (const char *)src);
        }

        // Struct elements with no string codec: there is no field metadata at
        // runtime to print them, so summarise rather than fail.
        if (parameter->element_type == ODIN_ELEMENT_TYPE_CUSTOM &&
            find_extension(parameter, ODIN_EXTENSION_TYPE_STRING_CODEC) == NULL) {
            return snprintf(output_buffer, output_buffer_size, "<%d elements x %u B (%s)>",
                            num_elements, parameter->element_size, "custom");
        }

        // Print all elements formatted in square brackets, streaming so the
        // length is bounded by the output buffer, not the input array size.
        int len = 0;
        output_buffer[len++] = '[';

        for (int i = 0; i < num_elements; i++) {
            const uint8_t *element = src + (size_t)i * parameter->element_size;
            int ret = ODIN_append_element_string(parameter, (void *)element, output_buffer, output_buffer_size, &len);
            if (ret < 0) {
                return ret;
            }

            // element did not fit: close with an ellipsis instead
            if (ret == 0) {
                len += snprintf(output_buffer + len, output_buffer_size - len, "...");
                break;
            }

            // if not last
            if (i < num_elements - 1) {
                output_buffer[len++] = ',';
                output_buffer[len++] = ' ';
            }
        }
        output_buffer[len++] = ']';
        output_buffer[len] = '\0';

        return len;
    }

    return ODIN_ERROR_NOT_SUPPORTED;
}
int ODIN_decode_string_to_parameter(const ODIN_parameter_t *parameter, const char *input_buffer,
                                    odin_access_group_t access_group) {
    // Only support writing to parameters for now, not vectors and arrays
    if (parameter->odin_type != ODIN_TYPE_PARAMETER) {
        return ODIN_ERROR_NOT_SUPPORTED;
    }

    // Decode the string to the parameter
    uint8_t data_buffer[ODIN_PRINT_BUFFER_SIZE];
    int ret = ODIN_string_to_element(parameter, input_buffer, data_buffer, sizeof(data_buffer));

    if (ret < 0) {
        return ret;
    }

    // Write the data to the parameter
    return ODIN_parameter_write(parameter, data_buffer, parameter->element_size, access_group);
}
