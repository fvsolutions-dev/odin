
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "odin_datastore.h"
#include "srv_logging.h"

const char *TAG = "ODIBN";

/**
 * @brief Method to find a ODIN group by name
 *
 * @param OD Pointer to the ODIN store
 * @param name Name of the group
 *
 * @return ODIN_parameter_group_t* Pointer to the group if found, NULL otherwise
 */
ODIN_parameter_group_t *ODIN_find_group_by_name(ODIN_store_t *OD, const char *name)
{
    for (int i = 0; i < OD->count; i++)
    {
        if (strcmp(OD->groups[i]->name, name) == 0)
        {
            return OD->groups[i];
        }
    }
    return NULL;
}

/**
 * @brief Method to find a ODIN group by ID
 *
 * @param OD Pointer to the ODIN store
 * @param index Index of the group
 *
 * @return ODIN_parameter_group_t* Pointer to the group if found, NULL otherwise
 */
ODIN_parameter_group_t *ODIN_find_group_by_id(ODIN_store_t *OD, uint16_t index)
{
    for (int i = 0; i < OD->count; i++)
    {
        if (OD->groups[i]->index == index)
        {
            return OD->groups[i];
        }
    }
    return NULL;
}

/**
 * @brief Method to find a ODIN parameter by name
 *
 * @param OD Pointer to the ODIN store
 * @param group_name Name of the group
 * @param parameter_name Name of the parameter
 *
 * @return ODIN_parameter_t* Pointer to the parameter if found, NULL otherwise
 */
ODIN_parameter_t *ODIN_find_parameter_by_name(ODIN_store_t *OD, const char *group_name, const char *parameter_name)
{
    ODIN_parameter_group_t *group = ODIN_find_group_by_name(OD, group_name);
    if (group == NULL)
    {
        return NULL;
    }

    for (int i = 0; i < group->count; i++)
    {
        if (strcmp(group->parameters[i]->name, parameter_name) == 0)
        {
            return group->parameters[i];
        }
    }

    return NULL;
}

/**
 * @brief Method to check if a parameter is accessible
 *
 * @param parameter Pointer to the parameter
 * @param access_group Access group
 * @param operation Operation to check
 */
bool ODIN_check_access(ODIN_parameter_t *parameter, uint16_t access_group, uint16_t operation)
{
    // Check if the parameter is valid
    if (parameter == NULL)
    {
        return false;
    }

    // Check if the operation is allowed
    if (!((access_group << operation) & parameter->access))
    {
        return false;
    }

    return true;
}

const char *ODIN_error_to_string(int error)
{
    switch (error)
    {
    case ODIN_SUCCESS:
        return "Success";
    case ODIN_ERROR_NO_PARAMETER:
        return "No parameter";
    case ODIN_ERROR_PARAMETER_NOT_FOUND:
        return "Parameter not found";
    case ODIN_ERROR_SIZE_MISMATCH:
        return "Size mismatch";
    case ODIN_ERROR_PERMISSION_DENIED:
        return "Permission denied";
    case ODIN_ERROR_UNSUPPORTED_FORMAT:
        return "Unsupported format";
    case ODIN_ERROR:
        return "General error";
    default:
        return "Unknown error";
    }
}

/**
 * @brief Method to find a ODIN parameter by ID
 *
 * @param OD Pointer to the ODIN store
 * @param index Index of the group
 * @param sub_index Sub index of the parameter
 *
 * @return ODIN_parameter_t* Pointer to the parameter if found, NULL otherwise
 */
ODIN_parameter_t *ODIN_find_parameter_by_id(ODIN_store_t *OD, uint32_t index)
{
    uint16_t group_index = (index >> 16) & 0xFFFF;

    ODIN_parameter_group_t *group = ODIN_find_group_by_id(OD, group_index);
    if (group == NULL)
    {
        return NULL;
    }

    for (int i = 0; i < group->count; i++)
    {
        if (group->parameters[i]->index == index)
        {
            return group->parameters[i];
        }
    }

    return NULL;
}

/**
 * @brief Method to read a parameter
 *
 * @param parameter Pointer to the parameter
 * @param data Pointer to the data buffer
 * @param size Size of the data buffer
 * @param access_group Access group
 *
 * @return int Size of the data read, or error code
 */
int ODIN_parameter_read(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    // Check if the parameter is valid
    if (parameter == NULL)
    {
        return ODIN_ERROR_NO_PARAMETER;
    }

    // Check if the size is correct
    if (size < parameter->size)
    {
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    // Check if the permission is allowed
    if (!ODIN_check_access(parameter, access_group, ODIN_READ_ACCESS))
    {
        return ODIN_ERROR_PERMISSION_DENIED;
    }

    // Copy the data to the buffer
    memcpy(data, parameter->data, parameter->size);

    // Log the access
    // log_parameter_access(parameter, ACCES_READ);

    return ODIN_SUCCESS;
}

/**
 * @brief Method to write a parameter
 *
 * @param parameter Pointer to the parameter
 * @param data Pointer to the data buffer
 * @param size Size of the data buffer
 * @param access_group Access group
 *
 * @return int Size of the data written, or error code
 */
int ODIN_parameter_write(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    if (parameter == NULL)
    {
        return ODIN_ERROR_NO_PARAMETER;
    }
    if (size != parameter->size)
    {
        return ODIN_ERROR_SIZE_MISMATCH;
    }
    if (!ODIN_check_access(parameter, access_group, ODIN_WRITE_ACCESS))
    {
        return ODIN_ERROR_PERMISSION_DENIED;
    }

    // Copy the data into the parameter
    memcpy(parameter->data, data, parameter->size);

    // Log the access
    // log_parameter_access(parameter, ACCES_WRITE);

    return ODIN_SUCCESS;
}

// int write_value_bool(ODIN_parameter_t *parameter, bool data)
// {
//     uint8_t value = data ? 1 : 0;
//     return write_value(parameter, &value, 1);
// }

// int write_value_uint8(ODIN_parameter_t *parameter, uint8_t data)
// {
//     return write_value(parameter, &data, 1);
// }

// int write_value_uint16(OD_parameter_t *parameter, uint16_t data)
// {
//     return write_value(parameter, &data, 2);
// }

int write_value_uint16(ODIN_parameter_t *parameter, uint16_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 2, access_group);
}

// int read_value_bool(OD_parameter_t *parameter, bool *data)
// {
//     uint8_t value;
//     int ret = read_value(parameter, &value, 1);
//     *data = value == 1;
//     return ret;
// }

// int read_value_uint8(OD_parameter_t *parameter, uint8_t *data)
// {
//     return read_value(parameter, data, 1);
// }

int read_value_uint16(ODIN_parameter_t *parameter, uint16_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 2, access_group);
}

// int read_value_int16(OD_parameter_t *parameter, int16_t *data)
// {
//     return read_value(parameter, data, 2);
// }

// int read_value_float(OD_parameter_t *parameter, float *data)
// {
//     return read_value(parameter, data, 4);
// }