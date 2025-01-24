#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>

extern "C" {
#include "encoding/encode_string.h"
#include "odin.h"
#include "odin_core.h"

}

// Group 0 RW
// Group 1 R
// Group 2 No access

uint32_t value = 0;
ODIN_parameter_t test_param = {
    .odin_type = ODIN_TYPE_PARAMETER,
    .element_type = ODIN_ELEMENT_TYPE_INT32,
    .flags = (ODIN_ACCESS_GROUP_0 & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_GROUP_1 & (ODIN_ACCESS_READ)),
    .element_size = sizeof(int32_t),
    .data = &value,
    .name_and_description = "test_variable_i32"};

// Single parameter tests
TEST(ODINParameterBasicAccess, Nominal) {
    int32_t output_data = 0;

    // clang-format off
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_0), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_1), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_2), ODIN_ERROR_PERMISSION_DENIED);

    EXPECT_GE(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_0), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_1), ODIN_ERROR_PERMISSION_DENIED);
    EXPECT_EQ(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_2), ODIN_ERROR_PERMISSION_DENIED);
    // clang-format on
}