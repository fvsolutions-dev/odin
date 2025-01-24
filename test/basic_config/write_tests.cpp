#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>
#include "odin.h"

extern "C" {
#include "OD.h"
#include "encoding/encode_string.h"
#include "odin_core.h"
}

static const ODIN_parameter_t* base_test_param = &root.test_variable_i32;
static const ODIN_parameter_t* base_array_param = &root.i32_array;
static const ODIN_parameter_t* base_vector_param = &root.i32_variable_length_array;

// Single parameter tests
TEST(ODINParameterWriteTest, Nominal) {
    int32_t input_data = 0x12345678;
    int result = ODIN_parameter_write(base_test_param, &input_data, sizeof(input_data), 0);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Check if the size is exactly the same
    EXPECT_EQ(sizeof(input_data), result);

    // Check if the value is correct
    EXPECT_EQ(input_data, root_ram.test_variable_i32);
}

TEST(ODINParameterWriteTest, Null) {
    int32_t input_data = 0x12345678;
    int result = ODIN_parameter_write(NULL, &input_data, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINParameterWriteTest, InvalidSize) {
    int32_t input_data = 0x12345678;
    int result = ODIN_parameter_write(base_test_param, &input_data, sizeof(input_data) - 1, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_write(base_test_param, &input_data, sizeof(input_data) + 1, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINParameterWriteTest, InvalidData) {
    int32_t input_data = 0x12345678;
    int result = ODIN_parameter_write(base_test_param, NULL, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

// Array tests
TEST(ODINArrayWriteTest, Nominal) {
    const int element_size = sizeof(root_ram.i32_array[0]);
    const int array_size_bytes = sizeof(root_ram.i32_array);
    const int array_size_elements = array_size_bytes / element_size;

    // Create a oversized array, to check if the last element is untouched
    int32_t input_data[array_size_elements + 1] = {0};
    for (int i = 0; i < array_size_elements + 1; i++) {
        input_data[i] = 0x12345678;
    }

    int result = ODIN_parameter_write(base_array_param, input_data, array_size_bytes, 0);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Check if the size is exactly the same
    EXPECT_EQ(array_size_bytes, result);

    // Check if the value is correct
    for (int i = 0; i < 10; i++) {
        EXPECT_EQ(input_data[i], root_ram.i32_array[i]);
    }

    // Check if the last element is untouched
    EXPECT_EQ(input_data[10], 0x12345678);
}

TEST(ODINArrayWriteTest, NullWrite) {
    int32_t input_data[10] = {0};
    int result = ODIN_parameter_write(NULL, input_data, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINArrayWriteTest, InvalidDataWrite) {
    int32_t input_data[10] = {0};
    int result = ODIN_parameter_write(base_array_param, NULL, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINArrayWriteTest, InvalidSizeWrite) {
    int32_t input_data[10] = {0};
    int result = ODIN_parameter_write(base_array_param, input_data, sizeof(input_data) - 1, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_write(base_array_param, input_data, sizeof(input_data) + 1, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);

    result = ODIN_parameter_write(base_array_param, input_data, 0, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

// Vector tests
TEST(ODINVectorWriteTest, Nominal) {
    // const int element_size = sizeof(root_ram.i32_variable_length_array.data[0]);
    const int num_elements = 10;
    // const int vector_size_bytes = element_size * num_elements;

    uint32_t input_data[10] = {0};
    for (int i = 0; i < num_elements; i++) {
        input_data[i] = i * 100;
    }

    int result = ODIN_parameter_write(base_vector_param, input_data, sizeof(input_data), 0);
    EXPECT_GE(result, ODIN_SUCCESS);

    // Check if the size is exactly the same
    EXPECT_EQ(sizeof(input_data), result);

    // Check if the value is correct
    for (int i = 0; i < num_elements; i++) {
        EXPECT_EQ(input_data[i], root_ram.i32_variable_length_array.data[i]);
    }

    // Check if the rest of the vector is untouched
    for (int i = num_elements; i < 50; i++) {
        EXPECT_EQ(root_ram.i32_variable_length_array.data[i], 0);
    }

    // Check if the number of elements is set correctly
    EXPECT_EQ(num_elements, root_ram.i32_variable_length_array.num_elements);

    // Swite zero size
    result = ODIN_parameter_write(base_vector_param, input_data, 0, 0);
    EXPECT_EQ(result, ODIN_SUCCESS);
}

TEST(ODINVectorWriteTest, NullWrite) {
    uint32_t input_data[10] = {0};
    int result = ODIN_parameter_write(NULL, input_data, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINVectorWriteTest, InvalidDataWrite) {
    uint32_t input_data[10] = {0};
    int result = ODIN_parameter_write(base_vector_param, NULL, sizeof(input_data), 0);
    EXPECT_EQ(result, ODIN_ERROR_INVALID_ARGUMENT);
}

TEST(ODINVectorWriteTest, InvalidSizeWrite) {
    uint32_t input_data[500] = {0};
    
    int result = ODIN_parameter_write(base_vector_param, input_data, sizeof(input_data) , 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}

TEST(ODINVectorWriteTest, InvalidElementSizeWrite) {
    uint32_t input_data[10] = {0};
    int result = ODIN_parameter_write(base_vector_param, input_data, 7, 0);
    EXPECT_EQ(result, ODIN_ERROR_SIZE_MISMATCH);
}
