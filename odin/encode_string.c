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
int ODIN_encode_to_string(ODIN_parameter_t *parameter, char *output, uint8_t size, uint16_t access_group)
{

    uint8_t buffer[128];
    if (parameter->size > sizeof(buffer))
    {
        LOG_ERR(TAG, "Parameter size is too large");
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    int ret = ODIN_parameter_read(parameter, buffer, parameter->size, access_group);
    if (ret != ODIN_SUCCESS)
    {
        return ret;
    }

    int len = 0;
    switch (parameter->format)
    {
    case ODIN_ENCODING_NUMBER:
        switch (parameter->type)
        {
        case ODIN_ELEMENT_TYPE_UINT8:
            len = snprintf(output, size, "%u", *(uint8_t *)buffer);
            break;
        case ODIN_ELEMENT_TYPE_INT8:
            len = snprintf(output, size, "%d", *(int8_t *)buffer);
            break;

        case ODIN_ELEMENT_TYPE_UINT16:
            len = snprintf(output, size, "%u", *(uint16_t *)buffer);
            break;
        case ODIN_ELEMENT_TYPE_INT16:
            len = snprintf(output, size, "%d", *(int16_t *)buffer);
            break;

        case ODIN_ELEMENT_TYPE_UINT32:
            len = snprintf(output, size, "%lu", *(uint32_t *)buffer);
            break;
        case ODIN_ELEMENT_TYPE_INT32:
            len = snprintf(output, size, "%ld", *(int32_t *)buffer);
            break;

        case ODIN_ELEMENT_TYPE_BOOL:
            len = snprintf(output, size, "%s", (*(bool *)buffer) ? "true" : "false");
            break;
            
        default:
            return ODIN_ERROR_UNSUPPORTED_FORMAT;
        }

        break;
    case ODIN_ENCODING_DECIMAL:
        switch (parameter->type)
        {
        case ODIN_ELEMENT_TYPE_FLOAT:
            len = snprintf(output, size, "%.5f", *(float *)buffer);
            break;
        case ODIN_ELEMENT_TYPE_DOUBLE:
            len = snprintf(output, size, "%.5f", *(double *)buffer);
            break;
        default:
            return ODIN_ERROR_UNSUPPORTED_FORMAT;
        }
        break;

    case ODIN_ENCODING_STRING:
        // Not assuming null terminated string
        len = snprintf(output, size, "%.*s", parameter->size, (char *)buffer);
        break;

    case ODIN_ENCODING_HEX:
        len = snprintf(output, size, "0x");
        for (int i = 0; i < parameter->size; i++)
        {
            len += snprintf(output + len, size - len, "%02X", ((uint8_t *)buffer)[i]);
        }
        break;
    default:
        return ODIN_ERROR_UNSUPPORTED_FORMAT;
    }

    return len;
}

/**
 * @brief Parse a string and write it to a parameter
 *
 * @param parameter Pointer to the parameter
 * @param input Pointer to the buffer to store the string, must be null terminated
 * @param access_group Access group to check if the parameter is accessible
 *
 * @return int Length of the string
 */
int ODIN_decode_from_string(ODIN_parameter_t *parameter, char *input, uint16_t access_group)
{
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
