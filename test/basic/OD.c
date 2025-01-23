#include "OD.h"

root_ram_t root_ram = {
    .test_variable_i8 = 10,
    .test_variable_i16 = 12,
    .test_variable_i32 = 15,
    .test_variable_i64 = 20,
    .test_variable_u8 = 1,
    .test_variable_u16 = 2,
    .test_variable_u32 = 3,
    .test_variable_u64 = 4,
    .i32_array = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
    .i32_variable_length_array = {
        .data = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
        .num_elements = 10
    }
};

const root_type_t root = {
    .test_variable_i8 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT8,
        .flags = 0,
        .index = 0x00000001,
        .element_size = sizeof(int8_t),
        .data = &root_ram.test_variable_i8,
        .name_and_description = "test_variable_i8\0A test variable of type signed 8 bit integer",
        .extension = NULL
    },
    .test_variable_i16 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT16,
        .flags = 0,
        .index = 0x00000002,
        .element_size = sizeof(int16_t),
        .data = &root_ram.test_variable_i16,
        .name_and_description = "test_variable_i16\0A test variable of type signed 16 bit integer",
        .extension = NULL
    },
    .test_variable_i32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .index = 0x00000003,
        .element_size = sizeof(int32_t),
        .data = &root_ram.test_variable_i32,
        .name_and_description = "test_variable_i32\0A test variable of type signed 32 bit integer",
        .extension = NULL
    },
    .test_variable_i64 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT64,
        .flags = 0,
        .index = 0x00000004,
        .element_size = sizeof(int64_t),
        .data = &root_ram.test_variable_i64,
        .name_and_description = "test_variable_i64\0A test variable of type signed 64 bit integer",
        .extension = NULL
    },
    .test_variable_u8 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT8,
        .flags = 0,
        .index = 0x00000005,
        .element_size = sizeof(uint8_t),
        .data = &root_ram.test_variable_u8,
        .name_and_description = "test_variable_u8\0A test variable of type unsigned 8 bit integer",
        .extension = NULL
    },
    .test_variable_u16 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .flags = 0,
        .index = 0x00000006,
        .element_size = sizeof(uint16_t),
        .data = &root_ram.test_variable_u16,
        .name_and_description = "test_variable_u16\0A test variable of type unsigned 16 bit integer",
        .extension = NULL
    },
    .test_variable_u32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .flags = 0,
        .index = 0x00000007,
        .element_size = sizeof(uint32_t),
        .data = &root_ram.test_variable_u32,
        .name_and_description = "test_variable_u32\0A test variable of type unsigned 32 bit integer",
        .extension = NULL
    },
    .test_variable_u64 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .index = 0x00000008,
        .element_size = sizeof(uint64_t),
        .data = &root_ram.test_variable_u64,
        .name_and_description = "test_variable_u64\0A test variable of type unsigned 64 bit integer",
        .extension = NULL
    },
    .i32_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .index = 0x0000000B,
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
        .index = 0x0000000C,
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
    .index = 0x00000000,
    .shift = 4,
    .count = 10,
    .parameters = {&root.test_variable_i8, &root.test_variable_i16, &root.test_variable_i32, &root.test_variable_i64, &root.test_variable_u8, &root.test_variable_u16, &root.test_variable_u32, &root.test_variable_u64, &root.i32_array, &root.i32_variable_length_array}
};
