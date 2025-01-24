#include "odin_core.h"

#include "string.h"

#define TAG "ODIN"

/**
 * @brief Method to read a parameter
 *
 * @param parameter Pointer to the parameter
 * @param data Pointer to the data buffer
 * @param size Size of the data to read, needs to be exactly the size of the
 * parameter in case of a parameter or array
 * @param access_group The access group, which is requesting the read
 *
 * @return if negative an error code is returned, otherwise the size of the data
 * read in bytes
 */
int ODIN_parameter_read(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group) {
    // Check if the parameter exists
    if (parameter == NULL || data == NULL) {
        return ODIN_ERROR_INVALID_ARGUMENT;
    }

    // Check if the permission is allowed
    // if (!ODIN_check_access(parameter, access_group, ODIN_READ_ACCESS))
    // {
    //     LOG_ERR(TAG, "Permission denied when reading %s",
    //     parameter->name_and_description); return ODIN_ERROR_PERMISSION_DENIED;
    // }

    // Handle the extension (TODO)
    // if (parameter->extension != NULL && parameter->extension->ops->read !=
    // NULL)
    // {
    //     int ret = parameter->extension->ops->read(parameter, data, size,
    //     access_group); if (ret)
    //     {
    //         LOG_ERR(TAG, "Extension read failed, error %d ,parameter %s", ret,
    //         parameter->name);
    //     }
    //     return ret;
    // }

    // Otherwise, copy the data to the buffer
    int read_size = ODIN_get_data_size(parameter);

    // Check if the size matches the read size
    if (parameter->odin_type == ODIN_TYPE_VECTOR) {
        if (size < read_size) {
            LOG_ERR(TAG, "Read size to small (%zu < %u) when reading %s", size, read_size,
                    parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        ODIN_vector_structure_t *vector_structure = (ODIN_vector_structure_t *)parameter->data;

        // Copy the data
        memcpy(data, vector_structure->data, read_size);

    } else {
        if (size != read_size) {
            LOG_ERR(TAG, "Read size mismatch (%zu != %u) when reading %s", size, parameter->element_size,
                    parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        memcpy(data, parameter->data, read_size);
    }

    // Log the access
    // ODIN_conditionally_log_access(parameter, access_group, ODIN_READ_ACCESS);

    return read_size;
}

int ODIN_parameter_read_into_buffer(const ODIN_parameter_t *parameter, void *output_buffer, size_t output_buffer_size,
                                    uint16_t access_group) {
    int total_size = ODIN_get_data_size(parameter);

    // Check if the buffer is large enough
    if (output_buffer_size < total_size) {
        LOG_ERR(TAG, "Buffer too small (%zu < %u) when reading %s", output_buffer_size, total_size,
                parameter->name_and_description);
        return ODIN_ERROR_SIZE_MISMATCH;
    }

    int e = ODIN_parameter_read(parameter, output_buffer, total_size, access_group);
    return e;
}

int ODIN_get_data_size(const ODIN_parameter_t *parameter) {
    if (parameter->odin_type == ODIN_TYPE_VECTOR) {
        uint16_t *num_elements = (uint16_t *)parameter->data;
        if (*num_elements > parameter->max_elements) {
            return parameter->element_size * parameter->max_elements;
        } else {
            return parameter->element_size * *num_elements;
        }
    } else if (parameter->odin_type == ODIN_TYPE_ARRAY) {
        return parameter->element_size * parameter->max_elements;
    } else {
        return parameter->element_size;
    }
}
/**
 * @brief Method to get the maximum data size of a parameter
 *
 * @param parameter Pointer to the parameter
 *
 * @return The maximum data size in bytes
 */
int ODIN_get_max_data_size(const ODIN_parameter_t *parameter) {
    switch (parameter->odin_type) {
        case ODIN_TYPE_VECTOR:
        case ODIN_TYPE_ARRAY:
            return parameter->element_size * parameter->max_elements;

        case ODIN_TYPE_PARAMETER:
            return parameter->element_size;

        case ODIN_TYPE_GROUP:
            return 0;
    }
}

/**
 * @brief Method to write a parameter
 *
 * @param parameter Pointer to the parameter
 * @param data Pointer to the data buffer
 * @param size Size of the data to write, needs to be exactly the size of the
 * parameter in case of a parameter or array
 * @param access_group The access group, which is requesting the write
 *
 * @return if negative an error code is returned, otherwise the size of the data
 * written in bytes
 */
int ODIN_parameter_write(const ODIN_parameter_t *parameter, const void *data, size_t size, uint16_t access_group) {
    // Check if all the parameters are valid
    if (parameter == NULL || data == NULL) {
        return ODIN_ERROR_INVALID_ARGUMENT;
    }

    // Check if the permission is allowed
    // if (!ODIN_check_access(parameter, access_group, ODIN_WRITE_ACCESS))
    // {
    //     LOG_ERR(TAG, "Permission denied when writing %s",
    //     parameter->name_and_description); return ODIN_ERROR_PERMISSION_DENIED;
    // }

    // Handle the extension (TODO)
    // if (parameter->extension != NULL && parameter->extension->ops->write !=
    // NULL)
    // {
    //     int ret = parameter->extension->ops->write(parameter, data, size,
    //     access_group); if (ret)
    //     {
    //         LOG_ERR(TAG, "Extension write failed, error %d ,parameter %s", ret,
    //         parameter->name);
    //     }
    //     return ret;
    // }

    // Otherwise, copy the data to the buffer
    int max_write_size = ODIN_get_max_data_size(parameter);

    // Check if the size matches the write size
    if (parameter->odin_type == ODIN_TYPE_VECTOR) {
        if (size > max_write_size) {
            LOG_ERR(TAG, "Write size to large (%zu > %u) when writing %s", size, max_write_size,
                    parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        // Check if a non fractional number of elements is written
        if (size % parameter->element_size != 0) {
            LOG_ERR(TAG, "Write size not a multiple of element size (%zu %% %u != 0) when writing %s", size,
                    parameter->element_size, parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        ODIN_vector_structure_t *vector_structure = (ODIN_vector_structure_t *)parameter->data;

        // Copy the data
        memcpy(vector_structure->data, data, size);

        // Update the element count
        vector_structure->num_elements = size / parameter->element_size;

    } else {
        
        if (size != max_write_size) {
            LOG_ERR(TAG, "Write size mismatch (%zu != %u) when writing %s", size, max_write_size,
                    parameter->name_and_description);
            return ODIN_ERROR_SIZE_MISMATCH;
        }

        memcpy(parameter->data, data, size);
    }

    // Log the access
    // ODIN_conditionally_log_access(parameter, access_group, ODIN_WRITE_ACCESS);

    return size;
}
