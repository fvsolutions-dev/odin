#include "odin.h"
#include <string.h>
#include <stdio.h>

#define TAG "ODIN"

int ODIN_parameter_read_into_buffer(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    // Check if the buffer is large enough
    if (size < parameter->size)
    {
        LOG_ERR(TAG, "Buffer too small (%zu < %u) when reading %s", size, parameter->size, parameter->name_and_description);
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    return ODIN_parameter_read(parameter, data, parameter->size, access_group);

}

/**
 * @brief Method to read a parameter
 *
 * @param parameter Pointer to the parameter
 * @param data Pointer to the data buffer
 * @param size Size of the data to read, needs to be exactly the size of the parameter in case of a parameter or array
 * @param access_group The access group, which is requesting the read
 *
 * @return if negative an error code is returned, otherwise the size of the data read in bytes
 */
int ODIN_parameter_read(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    // Check if the parameter exists
    if (parameter == NULL)
    {
        return ODIN_ERROR_NO_PARAMETER;
    }

    // Check if the permission is allowed
    // if (!ODIN_check_access(parameter, access_group, ODIN_READ_ACCESS))
    // {
    //     LOG_ERR(TAG, "Permission denied when reading %s", parameter->name_and_description);
    //     return ODIN_ERROR_PERMISSION_DENIED;
    // }

    // Handle the extension (TODO)
    // if (parameter->extension != NULL && parameter->extension->ops->read != NULL)
    // {
    //     int ret = parameter->extension->ops->read(parameter, data, size, access_group);
    //     if (ret)
    //     {
    //         LOG_ERR(TAG, "Extension read failed, error %d ,parameter %s", ret, parameter->name);
    //     }
    //     return ret;
    // }

    // Otherwise, copy the data to the buffer
    int read_size = 0;

    switch (parameter->odin_type)
    {
    case ODIN_TYPE_PARAMETER:

        // Check if the size is exactly the same
        if (size != parameter->size)
        {
            LOG_ERR(TAG, "Read size mismatch (%zu != %u) when reading %s", size, parameter->size, parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        // Copy the data to the buffer
        memcpy(data, parameter->data, parameter->size);
        read_size = parameter->size;
        break;

    case ODIN_TYPE_ARRAY:

        // Check if the size is exactly the same
        read_size = parameter->size * parameter->max_elements;
        if (size != read_size)
        {
            LOG_ERR(TAG, "Read size mismatch (%zu != %u) when reading %s", size, read_size, parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        // Copy the data to the buffer
        memcpy(data, parameter->data, read_size);
        break;

    case ODIN_TYPE_VECTOR:

        // Check if data fits in the buffer
        uint16_t *num_elements = (uint16_t *)parameter->data;
        read_size = *num_elements * parameter->size;

        if (size < read_size)
        {
            LOG_ERR(TAG, "Read size to little (%zu < %u) when reading %s", size, read_size, parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        // Copy the actual data in the buffer
        void *vector_data = (void *)((uint8_t *)parameter->data + sizeof(uint16_t));

        // Copy the data
        memcpy(data, vector_data, read_size);

        break;

    default:
        return ODIN_ERROR;
    }

    // Log the access
    // ODIN_conditionally_log_access(parameter, access_group, ODIN_READ_ACCESS);

    return read_size;
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
// int ODIN_parameter_write(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
// {
//     if (parameter == NULL)
//     {
//         return ODIN_ERROR_NO_PARAMETER;
//     }

//     if (size != parameter->size)
//     {
//         LOG_ERR(TAG, "Write size mismatch, (%d != %d), parameter '%s'", size, parameter->size, parameter->name);
//         return ODIN_ERROR_SIZE_MISMATCH;
//     }

//     if (!ODIN_check_access(parameter, access_group, ODIN_WRITE_ACCESS))
//     {
//         LOG_ERR(TAG, "Permission denied, parameter %s", parameter->name);
//         return ODIN_ERROR_PERMISSION_DENIED;
//     }

//     // Validate
//     if (parameter->extension != NULL && parameter->extension->ops->validate != NULL)
//     {
//         int rc = parameter->extension->ops->validate(parameter, data, size, access_group);
//         if (rc != ODIN_SUCCESS)
//         {
//             return rc;
//         }
//     }

//     if (parameter->extension != NULL && parameter->extension->ops->write != NULL)
//     {
//         int rc = parameter->extension->ops->write(parameter, data, size, access_group);
//         if (rc != ODIN_SUCCESS)
//         {
//             LOG_ERR(TAG, "Extension write failed, error %d ,parameter %s", rc, parameter->name);
//             return rc;
//         }
//     }
//     else
//     {
//         // Copy the data into the parameter
//         memcpy(parameter->data, data, parameter->size);

//         // Log the access
//         ODIN_conditionally_log_access(parameter, access_group, ODIN_WRITE_ACCESS);
//     }

//     return ODIN_SUCCESS;
// }