
#include "odin_datastore.h"
#include "srv_logging.h"

// #undef LOG_LEVEL
// #define LOG_LEVEL LOG_LEVEL_DEBUG

__attribute__((unused)) static const char *TAG = "ODIN_EXT";

int range_validator_float(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    range_parameter_t *range = (range_parameter_t *)parameter->extension->data;

    float value;
    int ret = ODIN_parameter_read_float(parameter, data, size, &value);
    if (ret)
    {
        return ret;
    }

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
    mapped_parameter_t *mapped_parameter = (mapped_parameter_t *)parameter->extension->data;

    // Get number from parameter
    float value;
    int ret = ODIN_parameter_read_float(mapped_parameter->reference, mapped_parameter->reference->data, mapped_parameter->reference->size, &value);
    if (ret)
    {
        return ret;
    }

    // Scale and offset
    value = value * mapped_parameter->scale + mapped_parameter->offset;

    // Copy to param
    ret = ODIN_parameter_write_float(parameter, data, size, value);
    if (ret)
    {
        return ret;
    }
    return 0;
}

int mapped_write(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group)
{
    mapped_parameter_t *mapped_parameter = (mapped_parameter_t *)parameter->extension->data;

    // Get number from parameter
    float value;
    int ret = ODIN_parameter_read_float(parameter, data, size, &value);
    if (ret)
    {
        return ret;
    }

    // Scale and offset
    value = (value - mapped_parameter->offset) / mapped_parameter->scale;

    // Do the original write
    uint8_t buffer[8];
    ret = ODIN_parameter_write_float(mapped_parameter->reference, buffer, mapped_parameter->reference->size, value);
    if (ret)
    {
        return ret;
    }

    return ODIN_parameter_write(mapped_parameter->reference, buffer, mapped_parameter->reference->size, access_group);
}

ODIN_extension_ops_t parameter_mapping_extension = {
    .read = mapped_read,
    .write = mapped_write,
};