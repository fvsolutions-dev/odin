
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "odin_datastore.h"
#include "srv_logging.h"
#include "odin/stdio_dump.h"

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

void ODIN_conditionally_log_access(ODIN_parameter_t *parameter, uint16_t access_group, uint16_t operation)
{
    extern uint32_t ODIN_access_log_values;
    // printf("op: %08X %d %08lX\n", access_group, operation, ODIN_access_log_values);
    if (!((access_group << operation) & ODIN_access_log_values))
    {
        return;
    }

    ODIN_log_parameter_access(parameter, operation == ODIN_READ_ACCESS ? "READ" : "WRITE", access_group);
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

    if (parameter->extension != NULL && parameter->extension->ops->read != NULL)
    {
        return parameter->extension->ops->read(parameter, data, size, access_group);
    }

    // Copy the data to the buffer
    memcpy(data, parameter->data, parameter->size);

    // Log the access
    ODIN_conditionally_log_access(parameter, access_group, ODIN_READ_ACCESS);

    return parameter->size;
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

    // Validate
    if (parameter->extension != NULL && parameter->extension->ops->validate != NULL)
    {
        int rc = parameter->extension->ops->validate(parameter, data, size, access_group);
        if (rc < 0)
        {
            return rc;
        }
    }

    if (parameter->extension != NULL && parameter->extension->ops->write != NULL)
    {
        int rc = parameter->extension->ops->write(parameter, data, size, access_group);
        if (rc < 0)
        {
            return rc;
        }
    }
    else
    {
        // Copy the data into the parameter
        memcpy(parameter->data, data, parameter->size);
    }

    // Log the access
    ODIN_conditionally_log_access(parameter, access_group, ODIN_WRITE_ACCESS);

    return ODIN_SUCCESS;
}

int ODIN_parameter_get_number(ODIN_parameter_t *parameter, const uint8_t *param_data, size_t param_size, float *data)
{
    LOG_DEBUG(TAG, "Checking size %d == %d", param_size, parameter->size);
    if (param_size != parameter->size)
    {
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    switch (parameter->type)
    {
    case ODIN_ELEMENT_TYPE_FLOAT:
        (*data) = *((float *)param_data);
        return sizeof(float);

    case ODIN_ELEMENT_TYPE_DOUBLE:
        (*data) = *((double *)param_data);
        return sizeof(double);

    case ODIN_ELEMENT_TYPE_INT8:
        (*data) = (float)(*((int8_t *)param_data));
        return sizeof(int8_t);

    case ODIN_ELEMENT_TYPE_UINT8:
        (*data) = (float)(*((uint8_t *)param_data));
        return sizeof(uint8_t);

    case ODIN_ELEMENT_TYPE_INT16:
        (*data) = (float)(*((int16_t *)param_data));
        return sizeof(int16_t);

    case ODIN_ELEMENT_TYPE_UINT16:
        (*data) = (float)(*((uint16_t *)param_data));
        return sizeof(uint16_t);

    case ODIN_ELEMENT_TYPE_INT32:
        (*data) = (float)(*((int32_t *)param_data));
        return sizeof(int32_t);

    case ODIN_ELEMENT_TYPE_UINT32:
        (*data) = (float)(*((uint32_t *)param_data));
        return sizeof(uint32_t);

    case ODIN_ELEMENT_TYPE_BOOL:
        (*data) = (float)(*((bool *)param_data));
        return sizeof(bool);

    default:
        return ODIN_ERROR;
    }
}

int ODIN_parameter_set_number(ODIN_parameter_t *parameter, uint8_t *buffer, size_t size, float data)
{
    LOG_DEBUG(TAG, "Checking size %d >= %d", size, parameter->size);

    if (size < parameter->size)
    {
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    switch (parameter->type)
    {
    case ODIN_ELEMENT_TYPE_FLOAT:
        *((float *)buffer) = data;
        return sizeof(float);

    case ODIN_ELEMENT_TYPE_DOUBLE:
        *((double *)buffer) = data;
        return sizeof(double);

    case ODIN_ELEMENT_TYPE_INT8:
        *((int8_t *)buffer) = (int8_t)data;
        return sizeof(int8_t);

    case ODIN_ELEMENT_TYPE_UINT8:
        *((uint8_t *)buffer) = (uint8_t)data;
        return sizeof(uint8_t);

    case ODIN_ELEMENT_TYPE_INT16:
        *((int16_t *)buffer) = (int16_t)data;
        return sizeof(int16_t);

    case ODIN_ELEMENT_TYPE_UINT16:
        *((uint16_t *)buffer) = (uint16_t)data;
        return sizeof(uint16_t);

    case ODIN_ELEMENT_TYPE_INT32:
        *((int32_t *)buffer) = (int32_t)data;
        return sizeof(int32_t);

    case ODIN_ELEMENT_TYPE_UINT32:
        *((uint32_t *)buffer) = (uint32_t)data;
        return sizeof(uint32_t);

    case ODIN_ELEMENT_TYPE_BOOL:
        *((bool *)buffer) = data;
        return sizeof(bool);

    default:
        return ODIN_ERROR;
    }
}

int ODIN_parameter_write_as_uint16(ODIN_parameter_t *parameter, uint16_t data, uint16_t access_group)
{
    if (parameter->type != ODIN_ELEMENT_TYPE_UINT16)
    {
        return ODIN_ERROR;
    }
    
    return ODIN_parameter_write(parameter, &data, 2, access_group);
}

int ODIN_parameter_read_as_uint16(ODIN_parameter_t *parameter, uint16_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 2, access_group);
}
int ODIN_parameter_write_as_int16(ODIN_parameter_t *parameter, int16_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 2, access_group);
}

int ODIN_parameter_read_as_int16(ODIN_parameter_t *parameter, int16_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 2, access_group);
}

int ODIN_parameter_write_as_uint32(ODIN_parameter_t *parameter, uint32_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 4, access_group);
}

int ODIN_parameter_read_as_uint32(ODIN_parameter_t *parameter, uint32_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 4, access_group);
}

int ODIN_parameter_write_as_int32(ODIN_parameter_t *parameter, int32_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 4, access_group);
}

int ODIN_parameter_read_as_int32(ODIN_parameter_t *parameter, int32_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 4, access_group);
}

int ODIN_parameter_write_as_float(ODIN_parameter_t *parameter, float data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 4, access_group);
}

int ODIN_parameter_read_as_float(ODIN_parameter_t *parameter, float *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 4, access_group);
}

int ODIN_parameter_write_as_uint8(ODIN_parameter_t *parameter, uint8_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 1, access_group);
}

int ODIN_parameter_read_as_uint8(ODIN_parameter_t *parameter, uint8_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 1, access_group);
}

int ODIN_parameter_write_as_int8(ODIN_parameter_t *parameter, int8_t data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 1, access_group);
}

int ODIN_parameter_read_as_int8(ODIN_parameter_t *parameter, int8_t *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 1, access_group);
}

int ODIN_parameter_write_as_bool(ODIN_parameter_t *parameter, bool data, uint16_t access_group)
{
    return ODIN_parameter_write(parameter, &data, 1, access_group);
}

int ODIN_parameter_read_as_bool(ODIN_parameter_t *parameter, bool *data, uint16_t access_group)
{
    return ODIN_parameter_read(parameter, data, 1, access_group);
}