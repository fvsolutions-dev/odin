#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "odin.pb.h"
#include "pb_decode.h"
#include "pb_encode.h"
#include "encode_string.h"
#include "odin_datastore.h"
#include "encode_protobuf.h"
#include "srv_logging.h"

static const char *TAG = "ODIBN";

static bool _encode_parameter(pb_ostream_t *stream, const pb_field_t *field, void *const *arg)
{
    parameter_encode_operation_t *operation = (parameter_encode_operation_t *)*arg;

    if (operation->parameter == NULL)
    {
        return false;
    }

    if (!pb_encode_tag_for_field(stream, field))
    {
        return false;
    }

    return pb_encode_string(stream, operation->parameter->data, operation->parameter->size);
}

void ODIN_protobuff_encode_init(ODIN_parameter_t *parameter, parameter_encode_operation_t *operation, uint16_t access_group)
{
    operation->access_group = access_group;
    operation->parameter = parameter;
    operation->proto.id = parameter->index;
    operation->proto.data.funcs.encode = _encode_parameter;
    operation->proto.data.arg = operation;
}

int ODIN_protobuff_export_to_stream(parameter_encode_operation_t *operation, pb_ostream_t *stream)
{
    int ret = pb_encode(stream, odin_proto_parameter_fields, &operation->proto);

    if (!ret)
    {
        return ODIN_ERROR;
    }

    return ODIN_SUCCESS;
}

int ODIN_protobuff_export_to_buffer(parameter_encode_operation_t *operation, uint8_t *buffer, size_t size)
{
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, size);
    int ret = pb_encode(&stream, odin_proto_parameter_fields, &operation->proto);

    if (!ret)
    {
        return ODIN_ERROR;
    }

    return stream.bytes_written;
}
bool _encode_collection(pb_ostream_t *stream, const pb_field_t *field, void *const *arg)
{
    parameter_collection_encode_operation_t *operation = (parameter_collection_encode_operation_t *)*arg;

    for (size_t index = 0; index < operation->count; index++)
    {
        ODIN_parameter_t *parameter = operation->parameters[index];

        // Add the proto parameter to the stream
        if (!pb_encode_tag_for_field(stream, field))
        {
            return false;
        }

        // Create the encode parameter operation
        parameter_encode_operation_t param_operation;
        ODIN_protobuff_encode_init(parameter, &param_operation, operation->access_group);

        // Encode the parameter
        if (!pb_encode_submessage(stream, odin_proto_parameter_fields, &param_operation.proto))
        {
            return false;
        }
    }
    return true;
}

void ODIN_protobuff_encode_collection_init(ODIN_parameter_t **parameter_buffer, size_t size, bool is_populated, parameter_collection_encode_operation_t *operation, uint16_t access_group)
{
    operation->parameters = parameter_buffer;
    operation->size = size;
    operation->count = is_populated ? size : 0;
    operation->proto.parameters.funcs.encode = _encode_collection;
    operation->proto.parameters.arg = operation;
}

int ODIN_protobuff_export_collection_to_buffer(parameter_collection_encode_operation_t *operation, uint8_t *buffer, size_t size)
{
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, size);
    int ret = pb_encode(&stream, odin_proto_parameter_collection_fields, &operation->proto);

    if (!ret)
    {
        return ODIN_ERROR;
    }

    return stream.bytes_written;
}

int ODIN_protobuff_export_collection_to_stream(parameter_collection_encode_operation_t *operation, pb_ostream_t *stream)
{
    int ret = pb_encode(stream, odin_proto_parameter_collection_fields, &operation->proto);

    if (!ret)
    {
        return ODIN_ERROR;
    }

    return ODIN_SUCCESS;
}

int ODIN_add_parameter_to_collection(parameter_collection_encode_operation_t *operation, ODIN_parameter_t *parameter)
{
    if (operation->count >= operation->size)
    {
        return ODIN_ERROR;
    }
    operation->parameters[operation->count++] = parameter;
    return ODIN_SUCCESS;
}

int ODIN_add_group_to_collection(parameter_collection_encode_operation_t *operation, ODIN_parameter_group_t *group)
{
    for (size_t index = 0; index < group->count; index++)
    {
        ODIN_parameter_t *parameter = group->parameters[index];
        int ret = ODIN_add_parameter_to_collection(operation, parameter);
        if (ret)
        {
            return ODIN_ERROR;
        }
    }
    return ODIN_SUCCESS;
}

int ODIN_add_store_to_collection(parameter_collection_encode_operation_t *operation, ODIN_store_t *store)
{
    for (size_t index = 0; index < store->count; index++)
    {
        ODIN_parameter_group_t *group = store->groups[index];
        int ret = ODIN_add_group_to_collection(operation, group);
        if (ret)
        {
            return ODIN_ERROR;
        }
    }
    return ODIN_SUCCESS;
}

bool _decode_parameter(pb_istream_t *stream, const pb_field_t *field, void **arg)
{
    parameter_decode_operation_t *operation = (parameter_decode_operation_t *)*arg;

    // read the data
    uint8_t buffer[128];
    size_t size = stream->bytes_left;

    if (!pb_read(stream, buffer, size))
    {
        LOG_ERR(TAG, "decode: Failed to read parameter data");
        return false;
    }

    // Find the parameter
    ODIN_parameter_t *parameter = ODIN_find_parameter_by_id(operation->store, operation->proto->id);
    if (parameter == NULL)
    {
        LOG_ERR(TAG, "decode: Failed to find parameter with id %ld", operation->proto->id);
        return false;
    }

    // Set the data
    if (ODIN_parameter_write(parameter, buffer, size, operation->access_group) != ODIN_SUCCESS)
    {
        LOG_ERR(TAG, "decode: Failed to set parameter");
        return false;
    }

    return true;
}

bool _decode_parameter_collection(pb_istream_t *stream, const pb_field_t *field, void **arg)
{
    parameter_collection_decode_operation_t *operation = (parameter_collection_decode_operation_t *)*arg;

    // Decode all parameters
    odin_proto_parameter proto_parameter = odin_proto_parameter_init_zero;
    proto_parameter.data.funcs.decode = _decode_parameter;

    parameter_decode_operation_t param_operation =
        {
            .access_group = operation->access_group,
            .store = operation->store,
            .proto = &proto_parameter,
        };

    proto_parameter.data.arg = &param_operation;

    // Decode all parameters
    while (pb_decode(stream, odin_proto_parameter_fields, &proto_parameter))
    {
    }

    return true;
}

int ODIN_protobuff_import_params_from_buffer(uint8_t *buffer, size_t size, ODIN_store_t *store, uint16_t access_group)
{
    pb_istream_t stream = pb_istream_from_buffer(buffer, size);
    return ODIN_protobuff_import_params_from_stream(&stream, store, access_group);
}

int ODIN_protobuff_import_params_from_stream(pb_istream_t *stream, ODIN_store_t *store, uint16_t access_group)
{
    parameter_collection_decode_operation_t operation;
    operation.access_group = access_group;
    operation.store = store;

    odin_proto_parameter_collection collection = odin_proto_parameter_collection_init_zero;
    collection.parameters.funcs.decode = _decode_parameter_collection;
    collection.parameters.arg = &operation;

    // Decode the collection
    bool ret = pb_decode(stream, odin_proto_parameter_collection_fields, &collection);
    if (!ret)
    {
        LOG_ERR(TAG, "Failed to decode parameter collection");
        return ODIN_ERROR;
    }

    return ODIN_SUCCESS;
}

static bool _file_read(pb_istream_t *stream, pb_byte_t *buf, size_t count)
{
    FILE *file = (FILE *)stream->state;
    size_t read = fread(buf, 1, count, file);
    return read == count;
}

int ODIN_protobuff_import_from_file(ODIN_store_t *store, const char *filename, uint16_t access_group)
{
    FILE *file = fopen(filename, "rb");
    if (file == NULL)
    {
        LOG_ERR(TAG, "Failed to open file %s", filename);
        return ODIN_ERR_FILE_NOT_FOUND;
    }

    // Determine the file size
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);

    pb_istream_t stream = {
        .callback = _file_read,
        .state = file,
        .bytes_left = size,
    };

    // Create a stream
    int ret = ODIN_protobuff_import_params_from_stream(&stream, store, access_group);
    fclose(file);

    if (ret != ODIN_SUCCESS)
    {
        LOG_ERR(TAG, "Failed to import parameters from file");
        return ODIN_ERROR;
    }

    return ODIN_SUCCESS;
}

static bool _file_write(pb_ostream_t *stream, const pb_byte_t *buf, size_t count)
{
    FILE *file = (FILE *)stream->state;
    size_t written = fwrite(buf, 1, count, file);
    return written == count;
}

int ODIN_protobuff_export_group_to_file(ODIN_parameter_group_t *group, const char *filename, uint16_t access_group)
{
    FILE *file = fopen(filename, "wb");
    if (file == NULL)
    {
        LOG_ERR(TAG, "Failed to open file %s", filename);
        return ODIN_ERROR;
    }

    pb_ostream_t stream = {
        .callback = _file_write,
        .state = file,
        .max_size = SIZE_MAX,
    };

    // Write the collection
    parameter_collection_encode_operation_t operation;
    ODIN_parameter_t *parameter_buffer[128];
    ODIN_protobuff_encode_collection_init(parameter_buffer, 128, false, &operation, access_group);
    ODIN_add_group_to_collection(&operation, group);

    // Encode the collection
    int ret = ODIN_protobuff_export_collection_to_stream(&operation, &stream);
    if (ret != ODIN_SUCCESS)
    {
        LOG_ERR(TAG, "Failed to encode parameter collection");
        return ret;
    }

    fclose(file);

    return ODIN_SUCCESS;
}


int ODIN_protobuff_export_store_to_file(ODIN_store_t *store, const char *filename, uint16_t access_group)
{
    FILE *file = fopen(filename, "wb");
    if (file == NULL)
    {
        LOG_ERR(TAG, "Failed to open file %s", filename);
        return ODIN_ERROR;
    }

    pb_ostream_t stream = {
        .callback = _file_write,
        .state = file,
        .max_size = SIZE_MAX,
    };

    // Write the collection
    parameter_collection_encode_operation_t operation;
    ODIN_parameter_t *parameter_buffer[128];
    ODIN_protobuff_encode_collection_init(parameter_buffer, 128, false, &operation, access_group);
    ODIN_add_store_to_collection(&operation, store);

    // Encode the collection
    int ret = ODIN_protobuff_export_collection_to_stream(&operation, &stream);
    if (ret != ODIN_SUCCESS)
    {
        LOG_ERR(TAG, "Failed to encode parameter collection");
        return ret;
    }

    fclose(file);

    return ODIN_SUCCESS;
}
