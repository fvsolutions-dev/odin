#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>

extern "C" {
#include "OD.h"
#include "odin.h"
#include "odin_codec.h"
#include "odin_core.h"
}

// Single parameter tests
TEST(ODINTestBytesCodec, NominalTest) {
    int32_t original_value = 123456;
    root_ram.test_variable_A = original_value;

    uint8_t buffer[128] = {0};
    int len = ODIN_encode_parameter_to_bytes(&root.test_variable_A, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(len, ODIN_SUCCESS);

    // Check if the size is what we expect
    EXPECT_EQ(sizeof(int32_t) + sizeof(uint32_t) + sizeof(uint16_t), len);

    // change the value to 0
    root_ram.test_variable_A = 0;

    // load the value from the buffer
    len = ODIN_decode_bytes_to_parameter(&odin_store, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(len, ODIN_SUCCESS);

    // Check if the value is correct
    EXPECT_EQ(original_value, root_ram.test_variable_A);
}

size_t encode_uint32_test_parameter(const ODIN_parameter_t *parameter, uint32_t target_value, uint8_t *buffer,
                                    size_t buffer_size) {
    EXPECT_GE(ODIN_parameter_write(parameter, &target_value, sizeof(target_value), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);

    // Encode the value
    int len = ODIN_encode_parameter_to_bytes(parameter, buffer, buffer_size, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(len, ODIN_SUCCESS);

    return len;
}

const uint32_t test_value = 0x12345678;

TEST(ODINTestBytesCodec, CorrupionTest) {
    for (int i = 0; i < 6; i++) {
        uint8_t buffer[128] = {0};
        int len = encode_uint32_test_parameter(&root.test_variable_A, test_value, buffer, sizeof(buffer));

        root_ram.test_variable_A = 0;

        buffer[i]++;
        // load the value from the buffer
        len = ODIN_decode_bytes_to_parameter(&odin_store, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);
        ASSERT_LT(len, ODIN_SUCCESS);

        // Check if the value has not changed
        EXPECT_EQ(root_ram.test_variable_A, 0);

        buffer[i] -= 2;

        // load the value from the buffer
        len = ODIN_decode_bytes_to_parameter(&odin_store, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);
        ASSERT_LT(len, ODIN_SUCCESS);

        // Check if the value has not changed
        EXPECT_EQ(root_ram.test_variable_A, 0);
    }
}

// Single parameter tests
TEST(ODINTestGroupBytesCodec, NominalTest) {
    // Copy the value to the RAM
    uint8_t ram_buffer[512];
    memcpy(ram_buffer, &root_ram, sizeof(root_ram));

    uint8_t buffer[256] = {0};
    int len = ODIN_encode_parameter_group_to_bytes(&odin_store, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(len, ODIN_SUCCESS);

    // Zero the RAM
    memset(&root_ram, 0, sizeof(root_ram));

    // load the value from the buffer
    len = ODIN_decode_bytes_to_parameter_group(&odin_store, buffer, len, ODIN_ACCESS_GROUP_INTERNAL);

    EXPECT_GE(len, ODIN_SUCCESS);

    // Check if the value is correct
    EXPECT_EQ(0, memcmp(ram_buffer, &root_ram, sizeof(root_ram)));
}

// Single parameter tests
TEST(ODINTestProtobuffCodec, NominalTest) {
    // Copy the contents to the RAM
    uint8_t ram_buffer[512];
    memcpy(ram_buffer, &root_ram, sizeof(root_ram));

    uint8_t encoded_buffer[256] = {0};
    parameter_group_encode_operation_t op;
    EXPECT_EQ(ODIN_encode_parameter_group_to_protobuff_init(&odin_store, &op, ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);

    int len = ODIN_encode_parameter_group_to_protobuff_buffer(&op, encoded_buffer, sizeof(encoded_buffer));
    EXPECT_GE(len, ODIN_SUCCESS);

    // Zero the RAM
    memset(&root_ram, 0, sizeof(root_ram));

    // load the value from the buffer
    len = ODIN_decode_protobuff_buffer_to_parameter_group(&odin_store, encoded_buffer, len, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(len, ODIN_SUCCESS);

    // Check if the value is correct
    EXPECT_EQ(0, memcmp(ram_buffer, &root_ram, sizeof(root_ram)));
}
