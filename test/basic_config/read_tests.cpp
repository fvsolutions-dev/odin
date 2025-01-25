#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>

extern "C" {
#include "OD.h"
#include "odin_codec.h"

#include "odin_core.h"
}

static const ODIN_parameter_t* base_test_param = &root.test_variable_i32;
static const ODIN_parameter_t* base_array_param = &root.i32_array;
static const ODIN_parameter_t* base_vector_param = &root.i32_variable_length_array;

TEST(ODINParameterReadTest, Nominal) {
    int32_t output_data = 0;
    int result = ODIN_parameter_read(base_test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Check if the size is exactly the same
    EXPECT_EQ(sizeof(output_data), result);

    // Check if the value is correct
    EXPECT_EQ(output_data, root_ram.test_variable_i32);
}

TEST(ODINParameterReadTest, Null) {
    int32_t output_data = 0;
    int result = ODIN_parameter_read(NULL, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterReadTest, InvalidSize) {
    int32_t output_data = 0;
    int result = ODIN_parameter_read(base_test_param, &output_data, sizeof(output_data) - 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_read(base_test_param, &output_data, sizeof(output_data) + 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINParameterReadTest, InvalidData) {
    int32_t output_data = 0;
    int result = ODIN_parameter_read(base_test_param, NULL, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINArrayReadTest, Nominal) {
    const int element_size = sizeof(root_ram.i32_array[0]);
    const int array_size_bytes = sizeof(root_ram.i32_array);

    int32_t output_data[(sizeof(root_ram.i32_array) / element_size) + 1] = {0};

    // Set last element to a non-zero value
    output_data[sizeof(root_ram.i32_array) / element_size] = 0x12345678;

    int result = ODIN_parameter_read(base_array_param, output_data, sizeof(output_data) - element_size, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Check if the size is exactly the same
    EXPECT_EQ(array_size_bytes, result);

    // Check if the value is correct
    for (int i = 0; i < 10; i++) {
        EXPECT_EQ(output_data[i], root_ram.i32_array[i]);
    }

    // Check if the last element is untouched
    EXPECT_EQ(output_data[10], 0x12345678);
}

TEST(ODINArrayReadTest, NullRead) {
    int32_t output_data[10] = {0};
    int result = ODIN_parameter_read(NULL, output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINArrayReadTest, InvalidDataRead) {
    int32_t output_data[10] = {0};
    int result = ODIN_parameter_read(base_array_param, NULL, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINArrayReadTest, InvalidSizeRead) {
    int32_t output_data[10] = {0};
    int result = ODIN_parameter_read(base_array_param, output_data, sizeof(output_data) - 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_read(base_array_param, output_data, sizeof(output_data) + 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_read(base_array_param, output_data, 0, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

// Vector tests
TEST(ODINVectorReadTest, Nominal) {
    const int element_size = sizeof(root_ram.i32_variable_length_array.data[0]);

    uint32_t data[256] = {0};

    // Set all the elements to a non-zero value
    for (int i = 0; i < sizeof(data) / sizeof(data[0]); i++) {
        data[i] = 0x12345678;
    }

    int result = ODIN_parameter_read(base_vector_param, data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Get the size of the data
    int size = ODIN_get_data_size(base_vector_param);
    EXPECT_EQ(size, result);

    // Check if the content is correct
    for (int i = 0; i < root_ram.i32_variable_length_array.num_elements; i++) {
        EXPECT_EQ(data[i], root_ram.i32_variable_length_array.data[i]);
    }

    // Check if the last element +1 is untouched
    EXPECT_EQ(data[root_ram.i32_variable_length_array.num_elements], 0x12345678);
}

TEST(ODINVectorReadTest, InvalidDataRead) {
    ODIN_vector_structure_t output_data = {0};
    int result = ODIN_parameter_read(base_vector_param, NULL, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINVectorReadTest, InvalidSizeRead) {
    ODIN_vector_structure_t output_data = {0};
    int result = ODIN_parameter_read(base_vector_param, &output_data, sizeof(output_data) - 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_read(base_vector_param, &output_data, sizeof(output_data) + 1, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_read(base_vector_param, &output_data, 0, ODIN_ACCESS_GROUP_INTERNAL);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}
