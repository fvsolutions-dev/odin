#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>

#include "odin.h"

extern "C" {
#include "OD.h"
#include "odin_codec.h"

#include "odin_core.h"
}

static const ODIN_parameter_t* base_array_param = &odin_objects.i32_array;

// Single parameter tests
TEST(ODINParameterArrayTest, ReadWriteElement) {
    // Reset array
    for (int i = 0; i < base_array_param->max_elements; i++) {
        odin_variables.i32_array[i] = 0;
    }

    // Read/Write elements separately
    for (int i = 0; i < base_array_param->max_elements; i++) {
        int32_t input_data = i * 100;
        int result = ODIN_array_write_element(base_array_param, i, &input_data, sizeof(input_data), ODIN_ACCESS_GROUP_INTERNAL);
        EXPECT_GE(result, ODIN_SUCCESS);

        // Check if the size is exactly the same
        EXPECT_EQ(sizeof(input_data), result);

        // Check if the value is correct
        EXPECT_EQ(input_data, odin_variables.i32_array[i]);
    
    
        // Read back the element
        int32_t output_data = 0;
        result = ODIN_array_read_element(base_array_param, i, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);

        // Check if the size is exactly the same
        EXPECT_EQ(sizeof(output_data), result);

        // Check if the value is correct
        EXPECT_EQ(input_data, output_data);
    }
}


// Not nominal tests
TEST(ODINParameterArrayTest, NullWriteElement) {
    int32_t input_data = 0x12345678;
    int result = ODIN_array_write_element(NULL, 0, &input_data, sizeof(input_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterArrayTest, NullDataWriteElement) {
    int result = ODIN_array_write_element(base_array_param, 0, NULL, sizeof(int32_t), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterArrayTest, InvalidSizeWriteElement) {
    int32_t input_data = 0x12345678;
    int result = ODIN_array_write_element(base_array_param, 0, &input_data, sizeof(input_data) - 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_array_write_element(base_array_param, 0, &input_data, sizeof(input_data) + 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINParameterArrayTest, OutOfBoundsWriteElement) {
    int32_t input_data = 0x12345678;
    int result = ODIN_array_write_element(base_array_param, base_array_param->max_elements, &input_data, sizeof(input_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINParameterArrayTest, NullReadElement) {
    int32_t output_data = 0;
    int result = ODIN_array_read_element(NULL, 0, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterArrayTest, NullDataReadElement) {
    int result = ODIN_array_read_element(base_array_param, 0, NULL, sizeof(int32_t), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterArrayTest, InvalidSizeReadElement) {
    int32_t output_data = 0;
    int result = ODIN_array_read_element(base_array_param, 0, &output_data, sizeof(output_data) - 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_array_read_element(base_array_param, 0, &output_data, sizeof(output_data) + 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINParameterArrayTest, OutOfBoundsReadElement) {
    int32_t output_data = 0;
    int result = ODIN_array_read_element(base_array_param, base_array_param->max_elements, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}
