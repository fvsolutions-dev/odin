#include "inttypes.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "encoding/encode_string.h"
#include "odin.h"

static const char *TAG = "ODIN_STR";

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
int ODIN_element_to_string(ODIN_element_type_t element_type, void *data,
                           char *output_buffer, size_t output_buffer_size) {

  int len = 0;
  switch (element_type) {

  case ODIN_ELEMENT_TYPE_UINT8:
    return snprintf(output_buffer, output_buffer_size, "%" PRIu8,
                    *(uint8_t *)data);

  case ODIN_ELEMENT_TYPE_INT8:
    return snprintf(output_buffer, output_buffer_size, "%" PRId8,
                    *(int8_t *)data);

  case ODIN_ELEMENT_TYPE_UINT16:
    return snprintf(output_buffer, output_buffer_size, "%" PRIu16,
                    *(uint16_t *)data);

  case ODIN_ELEMENT_TYPE_INT16:
    return snprintf(output_buffer, output_buffer_size, "%" PRId16,
                    *(int16_t *)data);

  case ODIN_ELEMENT_TYPE_UINT32:
    return snprintf(output_buffer, output_buffer_size, "%" PRIu32,
                    *(uint32_t *)data);

  case ODIN_ELEMENT_TYPE_INT32:
    return snprintf(output_buffer, output_buffer_size, "%" PRId32,
                    *(int32_t *)data);

  case ODIN_ELEMENT_TYPE_UINT64:
    return snprintf(output_buffer, output_buffer_size, "%" PRIu64,
                    *(uint64_t *)data);

  case ODIN_ELEMENT_TYPE_INT64:
    return snprintf(output_buffer, output_buffer_size, "%" PRId64,
                    *(int64_t *)data);

  case ODIN_ELEMENT_TYPE_BOOL:
    return snprintf(output_buffer, output_buffer_size, "%s",
                    (*(bool *)data) ? "true" : "false");

  case ODIN_ELEMENT_TYPE_FLOAT32:
    return snprintf(output_buffer, output_buffer_size, "%f", *(float *)data);

  case ODIN_ELEMENT_TYPE_FLOAT64:
    return snprintf(output_buffer, output_buffer_size, "%f", *(double *)data);

  case ODIN_ELEMENT_TYPE_HEX:
    return snprintf(output_buffer, output_buffer_size, "0x%02x",
                    *(uint8_t *)data);

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
int ODIN_encode_to_string(const ODIN_parameter_t *parameter,
                          char *output_buffer, size_t output_buffer_size,
                          uint16_t access_group) {

  uint8_t buffer[128];
  int ret = ODIN_parameter_read_into_buffer(parameter, buffer, sizeof(buffer),
                                            access_group);
  if (ret < 0) {
    return ret;
  }

  switch (parameter->odin_type) {
  case ODIN_TYPE_PARAMETER:
    return ODIN_element_to_string(parameter->element_type, buffer,
                                  output_buffer, output_buffer_size);

  case ODIN_TYPE_VECTOR:
    // Print all elements in the vector
    {
      uint16_t *num_elements = (uint16_t *)buffer;
      uint8_t *vector_data = buffer + sizeof(uint16_t);
      int len = 0;
      for (int i = 0; i < *num_elements; i++) {
        len += ODIN_element_to_string(
            parameter->element_type, vector_data + i * parameter->element_size,
            output_buffer + len, output_buffer_size - len);
        if (i < *num_elements - 1) {
          len += snprintf(output_buffer + len, output_buffer_size - len, ", ");
        }
      }
      return len;
    }

  case ODIN_TYPE_ARRAY:
    // Print all elements in the array
    {
      int len = 0;
      for (int i = 0; i < parameter->max_elements; i++) {
        len += ODIN_element_to_string(
            parameter->element_type, buffer + i * parameter->element_size,
            output_buffer + len, output_buffer_size - len);
        if (i < parameter->max_elements - 1) {
          len += snprintf(output_buffer + len, output_buffer_size - len, ", ");
        }
      }
      return len;
    }
  default:
    return ODIN_ERROR_NOT_SUPPORTED;
  }
}

/**
 * @brief Parse a string and write it to a parameter
 *
 * @param parameter Pointer to the parameter
 * @param input Pointer to the buffer to store the string, must be null
 * terminated
 * @param access_group Access group to check if the parameter is accessible
 *
 * @return int Length of the string
 */
int ODIN_decode_from_string(const ODIN_parameter_t *parameter, char *input,
                            uint16_t access_group) {
  return ODIN_ERROR_NOT_SUPPORTED;
#if 0

    if (parameter == 0)
    {
        return ODIN_ERROR_NO_PARAMETER;
    }

    if (!ODIN_check_access(parameter, access_group, ODIN_WRITE_ACCESS))
    {
        return ODIN_ERROR_PERMISSION_DENIED;
    }
    switch (parameter->format)
    {
    case ODIN_ENCODING_INT:
        if (parameter->size == 1)
            *(int8_t *)parameter->data = strtol(input, NULL, 0);
        else if (parameter->size == 2)
            *(int16_t *)parameter->data = strtol(input, NULL, 0);
        else if (parameter->size == 4)
            *(int32_t *)parameter->data = strtol(input, NULL, 0);
        break;

    case ODIN_ENCODING_UINT:
        if (parameter->size == 1)
            *(uint8_t *)parameter->data = strtoul(input, NULL, 0);
        else if (parameter->size == 2)
            *(uint16_t *)parameter->data = strtoul(input, NULL, 0);
        else if (parameter->size == 4)
            *(uint32_t *)parameter->data = strtoul(input, NULL, 0);
        break;

    case ODIN_ENCODING_FLOAT:
        if (parameter->size == 4)
            *(float *)parameter->data = strtof(input, NULL);
        else if (parameter->size == 8)
            *(double *)parameter->data = strtod(input, NULL);
        break;

    case ODIN_ENCODING_UTF8:
        // Here we assume that the data is a null terminated string
        strncpy((char *)parameter->data, input, parameter->size);
        break;

    case ODIN_ENCODING_HEX_LSB:

        // Check if the input is a valid hex string

        if (input[0] == '0' && (input[1] == 'x' || input[1] == 'X'))
        {
            input += 2;
        }

        if (strlen(input) != parameter->size * 2)
        {
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        for (int i = 0; i < parameter->size; i++)
        {
            char byte[3];
            byte[0] = input[i * 2];
            byte[1] = input[i * 2 + 1];
            byte[2] = 0;
            ((uint8_t *)parameter->data)[i] = strtol(byte, NULL, 16);
        }
        break;

    case ODIN_ENCODING_HEX:
    case ODIN_ENCODING_HEX_MSB:

        // Check if the input is a valid hex string

        if (input[0] == '0' && (input[1] == 'x' || input[1] == 'X'))
        {
            input += 2;
        }

        if (strlen(input) != parameter->size * 2)
        {
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        for (int i = parameter->size - 1; i >= 0; i--)
        {
            char byte[3];
            byte[0] = input[i * 2];
            byte[1] = input[i * 2 + 1];
            byte[2] = 0;
            ((uint8_t *)parameter->data)[i] = strtol(byte, NULL, 16);
        }
        break;

    case ODIN_ENCODING_NONE:
    default:
        return ODIN_ERROR_UNSUPPORTED_FORMAT;
    }
#endif
  return ODIN_SUCCESS;
}
