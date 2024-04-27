#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "odin_datastore.h"
#include "encode_string.h"
#include "srv_logging.h"

static const char *TAG = "ODIN_STR";

/**
 * @brief Serialise a parameter to a human readable string
 *
 * @param parameter Pointer to the parameter
 * @param output Pointer to the buffer to store the string
 * @param size Size of the buffer
 * @param access_group Access group to check if the parameter is accessible
 *
 * @return int Length of the string
 */
int ODIN_read_as_string(ODIN_parameter_t *parameter, char *output, uint8_t size, uint16_t access_group)
{
    if (parameter == 0)
    {
        return ODIN_ERROR_NO_PARAMETER;
    }

    if (!ODIN_check_access(parameter, access_group, ODIN_READ_ACCESS))
    {
        return ODIN_ERROR_PERMISSION_DENIED;
    }

    int len = 0;
    switch (parameter->format)
    {

    case ODIN_ENCODING_INT:
        if (parameter->size == 1)
            len = snprintf(output, size, "%02X", *(int8_t *)parameter->data);
        else if (parameter->size == 2)
            len = snprintf(output, size, "%04X", *(int16_t *)parameter->data);
        else if (parameter->size == 4)
            len = snprintf(output, size, "%08lX", *(int32_t *)parameter->data);
        break;

    case ODIN_ENCODING_UINT:
        if (parameter->size == 1)
            len = snprintf(output, size, "%u", *(uint8_t *)parameter->data);
        else if (parameter->size == 2)
            len = snprintf(output, size, "%u", *(uint16_t *)parameter->data);
        else if (parameter->size == 4)
            len = snprintf(output, size, "%lu", *(uint32_t *)parameter->data);
        break;

    case ODIN_ENCODING_FLOAT:
        if (parameter->size == 4)
            len = snprintf(output, size, "%f", *(float *)parameter->data);
        else if (parameter->size == 8)
            len = snprintf(output, size, "%f", *(double *)parameter->data);
        break;

    case ODIN_ENCODING_UTF8:
        // Here we assume that the data is a null terminated string
        len = snprintf(output, size, "%s", (char *)parameter->data);
        break;

    case ODIN_ENCODING_HEX_LSB:
        len = snprintf(output, size, "0x");
        for (int i = 0; i < parameter->size; i++)
        {
            len += snprintf(output + len, size - len, "%02X", ((uint8_t *)parameter->data)[i]);
        }
        break;

    case ODIN_ENCODING_HEX:
    case ODIN_ENCODING_HEX_MSB:
        len = snprintf(output, size, "0x");
        for (int i = parameter->size - 1; i >= 0; i--)
        {
            len += snprintf(output + len, size - len, "%02X", ((uint8_t *)parameter->data)[i]);
        }
        break;

    case ODIN_ENCODING_NONE:
    default:
        len = snprintf(output, size, "No printable format for data");
        break;
    }

    return len;
}
/**
 * @brief Ingest a parameter from a human readable string
 *
 * @param parameter Pointer to the parameter
 * @param input Pointer to the buffer to store the string, must be null terminated
 * @param access_group Access group to check if the parameter is accessible
 *
 * @return int Length of the string
 */
int ODIN_write_to_string(ODIN_parameter_t *parameter, char *input, uint16_t access_group)
{
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
    return ODIN_SUCCESS;
}
