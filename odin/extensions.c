
#include "odin_datastore.h"
#include "srv_logging.h"

static const char *TAG = "ODIN_EXT";

int range_validator_float(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    LOG_DEBUG(TAG, "Range validator");
    LOG_DEBUG(TAG, "Parameter name: %s", parameter->name);

    range_parameter_t *range = (range_parameter_t *)parameter->extension->data;
    LOG_DEBUG(TAG, "Range: %f - %f", range->min, range->max);

    float value;
    int rc = ODIN_parameter_get_number(parameter, data, size, &value);
    if (rc < 0)
    {
        return rc;
    }
    LOG_DEBUG(TAG, "Value: %f", value);

    if (value < range->min || value > range->max)
    {
        return ODIN_ERROR;
    }

    return ODIN_SUCCESS;
}

ODIN_extension_ops_t range_validator_extension = {
    .validate = range_validator_float,
};

int mapped_read(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    LOG_DEBUG(TAG, "Mapped read");
    LOG_DEBUG(TAG, "Parameter name: %s", parameter->name);

    mapped_parameter_t *mapped_parameter = (mapped_parameter_t *)parameter->extension->data;

    // Get number from parameter
    float value = 0;
    int rc = ODIN_parameter_get_number(mapped_parameter->reference, mapped_parameter->reference->data, mapped_parameter->reference->size, &value);
    if (rc < 0)
    {
        return rc;
    }

    // Scale and offset
    value = value * mapped_parameter->scale + mapped_parameter->offset;

    LOG_DEBUG(TAG, "Mapped value: %f", value);

    // Copy to param
    return ODIN_parameter_set_number(parameter, data, size, value);
}

int mapped_write(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    LOG_DEBUG(TAG, "Mapped write");
    LOG_DEBUG(TAG, "Parameter name: %s", parameter->name);
    mapped_parameter_t *mapped_parameter = (mapped_parameter_t *)parameter->extension->data;

    // Get number from parameter
    float value = -1;
    int rc = ODIN_parameter_get_number(parameter, data, size, &value);
    if (rc < 0)
    {
        return rc;
    }
    LOG_DEBUG(TAG, "GOot value: %f", value);

    // Scale and offset
    value = (value - mapped_parameter->offset) / mapped_parameter->scale;
    LOG_DEBUG(TAG, "Mapped value: %f", value);

    // Do the original write
    uint8_t buffer[8];
    int ret = ODIN_parameter_set_number(mapped_parameter->reference, buffer, mapped_parameter->reference->size, value);
    if (ret != ODIN_SUCCESS)
    {
        return ret;
    }

    return ODIN_parameter_write(mapped_parameter->reference, buffer, mapped_parameter->reference->size, access_group);
}

ODIN_extension_ops_t parameter_mapping_extension = {
    .read = mapped_read,
    .write = mapped_write,
};