#include "OD.h"

root_ram_t root_ram = {
    .test_variable_i32 = 15,
    .i32_array = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
    .i32_variable_length_array = {
        .data = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
        .num_elements = 10
    }
};

const root_type_t root = {
    .test_variable_i32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x01000000,
        .element_size = sizeof(int32_t),
        .data = &root_ram.test_variable_i32,
        .name_and_description = "test_variable_i32\0A test variable of type signed 32 bit integer",
        .extension = NULL
    },
    .i32_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x02000000,
        .element_size = sizeof(int32_t),
        .data = &root_ram.i32_array,
        .name_and_description = "i32_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .i32_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x03000000,
        .element_size = sizeof(int32_t),
        .data = &root_ram.i32_variable_length_array,
        .name_and_description = "i32_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 3,
    .parameters = {&root.test_variable_i32, &root.i32_array, &root.i32_variable_length_array}
};
