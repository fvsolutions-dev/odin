
#if 0

#include <string.h>
#include "odin/stdio_dump.h"
#include "odin/encode_string.h"
#include "odin/encode_protobuf.h"
#include "odin_datastore.h"
#include <pb_decode.h>
#include <pb_encode.h>
#include "srv_logging.h"

// Disabled

#include "app_datastore/output.h"

static const char *TAG = "ODIN_TEST";

ODIN_parameter_t *test_parameter = &ODIN_params.device_information.device_id;
uint16_t *internal_test_parameter_reference = &ODIN_ram.device_information.device_id;
uint8_t test_buffer[2048];

static void dump_hex(const uint8_t *buffer, int len)
{
    printf("Encoded %d bytes\n", len);
    for (int i = 0; i < len; i++)
    {
        printf("%02X ", buffer[i]);
    }
    printf("\n");
}

static int measure_encoding_time(parameter_collection_encode_operation_t *operation)
{
    // No timing functions available, TBC
    // int64_t start_time = esp_timer_get_time();
    ODIN_protobuff_export_collection_to_buffer(operation, (uint8_t *)test_buffer, sizeof(test_buffer));
    // int64_t end_time = esp_timer_get_time();
    return -1;
    // return end_time - start_time;
}

void test_dump()
{

    LOG_INFO(TAG, "Testing dump");
    ODIN_dump(&ODIN_store, true, ODIN_ACCESS_INTERNAL);
}

void test_dump_single_parameter()
{
    ODIN_dump_parameter(test_parameter, false, ODIN_ACCESS_INTERNAL);
}

void test_direct_access()
{

    LOG_INFO(TAG, "Testing direct access");
    ODIN_parameter_t *test_parameter = &ODIN_params.device_information.device_id;

    // Dump parameter
    ODIN_dump_parameter(test_parameter, false, ODIN_ACCESS_INTERNAL);

    // Increment the device id
    uint16_t data;
    ODIN_parameter_read_as_uint16(test_parameter, &data, ODIN_ACCESS_INTERNAL);
    data++;
    ODIN_parameter_write_as_uint16(test_parameter, data, ODIN_ACCESS_INTERNAL);

    // Dump parameter
    ODIN_dump_parameter(test_parameter, false, ODIN_ACCESS_INTERNAL);

    // Check if the value was incremented
    uint16_t readback_data = 0;
    ODIN_parameter_read_as_uint16(test_parameter, &readback_data, ODIN_ACCESS_INTERNAL);

    assert(readback_data == data);
}

void test_access_control()
{
    LOG_INFO(TAG, "Testing access control");
    ODIN_parameter_t *test_parameter = &ODIN_params.device_information.device_id;
    uint16_t *internal_reference = &ODIN_ram.device_information.device_id;

    // Set internal reference to known value
    *internal_reference = 0xF0F0;

    uint16_t read_data = 0xBEEF;

    assert(ODIN_parameter_read_as_uint16(test_parameter, &read_data, NULL) == ODIN_ERROR_PERMISSION_DENIED);
    assert(read_data == 0xBEEF);

    assert(ODIN_parameter_write_as_uint16(test_parameter, 0xDEAD, NULL) == ODIN_ERROR_PERMISSION_DENIED);
    assert(*internal_reference == 0xF0F0);

    assert(ODIN_parameter_read_as_uint16(test_parameter, &read_data, ODIN_ACCESS_INTERNAL) == ODIN_SUCCESS);
    assert(read_data == 0xF0F0);

    assert(ODIN_parameter_write_as_uint16(test_parameter, 0xDEAD, ODIN_ACCESS_INTERNAL) == ODIN_SUCCESS);
    assert(*internal_reference == 0xDEAD);
}

void test_parameter_string_serialisation()
{
    LOG_INFO(TAG, "Testing parameter string serialisation");

    // Set internal reference to known value
    *internal_test_parameter_reference = 0xDEAD;

    // Serialise the parameter
    char buffer[32];
    int len = ODIN_read_as_string(test_parameter, buffer, sizeof(buffer), ODIN_ACCESS_INTERNAL);
    assert(len > 0);

    // Check the serialised value was serialised correctly
    assert(strcmp(buffer, "0xDEAD") == 0);
}

void test_parameter_protobuff_buffer_serialisation()
{
    LOG_INFO(TAG, "Testing parameter proto serialisation");

    parameter_encode_operation_t operation;
    ODIN_protobuff_encode_init(test_parameter, &operation, ODIN_ACCESS_INTERNAL);

    // Serialise the parameter
    uint8_t buffer[32];
    assert(ODIN_protobuff_export_to_buffer(&operation, buffer, sizeof(buffer)) >= 0);

    dump_hex(buffer, sizeof(buffer));
}

void test_parameter_protobuff_buffer_collection_serialisation()
{
    LOG_INFO(TAG, "Testing parameter proto serialisation");

    ODIN_parameter_t *test_parameters[] = {
        &ODIN_params.device_information.device_name,
        &ODIN_params.device_information.manufacturer_id,
        &ODIN_params.device_information.system_harwdare_revision,
        &ODIN_params.trainer_configuration_1.configured_resistance};

    int param_count = sizeof(test_parameters) / sizeof(ODIN_parameter_t *);
    parameter_collection_encode_operation_t operation;
    ODIN_protobuff_encode_collection_init(test_parameters, param_count, true, &operation, ODIN_ACCESS_INTERNAL);

    LOG_INFO(TAG, "Added %d parameters to collection", operation.count);

    // Serialise the parameter
    int len = ODIN_protobuff_export_collection_to_buffer(&operation, test_buffer, sizeof(test_buffer));
    if (len < 0)
    {
        LOG_ERR(TAG, "Failed to encode parameter group");
        assert(false);
    }
    dump_hex((uint8_t *)test_buffer, len);
}

void test_parameter_group_serialisation()
{
    LOG_INFO(TAG, "Testing parameter group serialisation");

    ODIN_parameter_t *test_parameters[256];
    parameter_collection_encode_operation_t operation;
    ODIN_protobuff_encode_collection_init(test_parameters, sizeof(test_parameters) / sizeof(ODIN_parameter_t *), false, &operation, ODIN_ACCESS_INTERNAL);

    // Add group to the collection
    ODIN_add_group_to_collection(&operation, &ODIN_store_device_information);

    // Add store to the collection
    ODIN_add_store_to_collection(&operation, &ODIN_store);

    // Serialise the parameter
    int len = ODIN_protobuff_export_collection_to_buffer(&operation, (uint8_t *)test_buffer, sizeof(test_buffer));
    if (len < 0)
    {
        LOG_ERR(TAG, "Failed to encode parameter group");
        assert(false);
    }

    dump_hex((uint8_t *)test_buffer, len);
}

void test_protobuff_encoding_time()
{
    LOG_INFO(TAG, "Testing protobuff encoding time");

    ODIN_parameter_t *test_parameters[256];
    parameter_collection_encode_operation_t operation;
    ODIN_protobuff_encode_collection_init(test_parameters, sizeof(test_parameters) / sizeof(ODIN_parameter_t *), false, &operation, ODIN_ACCESS_INTERNAL);
    ODIN_add_store_to_collection(&operation, &ODIN_store);
    int time = measure_encoding_time(&operation);
    printf("Encoding all (%d) parameters took %d us\n", operation.count, time);

    parameter_collection_encode_operation_t single_param_operation;
    ODIN_protobuff_encode_collection_init(test_parameters, sizeof(test_parameters) / sizeof(ODIN_parameter_t *), false, &single_param_operation, ODIN_ACCESS_INTERNAL);
    ODIN_add_parameter_to_collection(&single_param_operation, &ODIN_params.device_information.device_id);
    time = measure_encoding_time(&single_param_operation);
    printf("Encoding single uint16_t parameter took %d us\n", time);
}

void test_decoding()
{
    LOG_INFO(TAG, "Testing decoding");
    uint8_t test_vector[] = {
        0x1A, 0x10, 0x08, 0x03, 0x12, 0x0C, 0x4D, 0x75, 0x6F, 0x76, 0x20, 0x62, 0x69, 0x6B, 0x65, 0x00, 0x00, 0x00, 0x1A, 0x06, 0x08, 0x08, 0x12, 0x02, 0x21, 0x43, 0x1A, 0x09, 0x08, 0x06, 0x12, 0x05, 0x75, 0x6E, 0x6B, 0x00, 0x00, 0x1A, 0x09, 0x08, 0x82, 0x80, 0x80, 0x01, 0x12, 0x02, 0x00, 0x00};
    pb_istream_t stream = pb_istream_from_buffer(test_vector, sizeof(test_vector));

    assert(ODIN_protobuff_import_params_from_stream(&stream, &ODIN_store, ODIN_ACCESS_INTERNAL) == ODIN_SUCCESS);
}

void test_encoding_decoding_all()
{
    LOG_INFO(TAG, "Testing encoding and decoding all parameters");
    ODIN_parameter_t *test_parameters[256];
    parameter_collection_encode_operation_t operation;
    // Encode parameters
    ODIN_protobuff_encode_collection_init(test_parameters, sizeof(test_parameters) / sizeof(ODIN_parameter_t *), false, &operation, ODIN_ACCESS_INTERNAL);
    ODIN_add_store_to_collection(&operation, &ODIN_store);
    int len = ODIN_protobuff_export_collection_to_buffer(&operation, (uint8_t *)test_buffer, sizeof(test_buffer));

    // Decode parameters
    if (ODIN_protobuff_import_params_from_buffer((uint8_t *)test_buffer, len, &ODIN_store, ODIN_ACCESS_INTERNAL))
    {
        LOG_ERR(TAG, "Failed to decode parameters");
        assert(false);
    }
}

#endif