#include "OD.h"

root_ram_t root_ram = {
    .test_variable_i8 = 0,
    .test_variable_i16 = 0,
    .test_variable_i32 = 0,
    .test_variable_i64 = 0,
    .test_variable_u8 = 0,
    .test_variable_u16 = 0,
    .test_variable_u32 = 0,
    .test_variable_u64 = 0,
    .test_variable_float32 = 0.40,
    .test_variable_float64 = 0.0,
    .test_variable_bool_false = false,
    .test_variable_bool_true = true,
    .test_variable_char = 'a',
    .group_A = {
        .group_A = {
            .other_child = 0.0},
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88},
    .test_variable_small = 86080530548};

const root_type_t root = {
    .test_variable_i8 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT8,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(int8_t),
        .data = &root_ram.test_variable_i8,
        .name_and_description = "test_variable_i8\0A test variable of type signed 8 bit integer",
        .extension = NULL},
    .test_variable_i16 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_INT16, .flags = 0, .index = 0x00000002, .size = sizeof(int16_t), .data = &root_ram.test_variable_i16, .name_and_description = "test_variable_i16\0A test variable of type signed 16 bit integer", .extension = NULL},
    .test_variable_i32 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_INT32, .flags = 0, .index = 0x00000003, .size = sizeof(int32_t), .data = &root_ram.test_variable_i32, .name_and_description = "test_variable_i32\0A test variable of type signed 32 bit integer", .extension = NULL},
    .test_variable_i64 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_INT64, .flags = 0, .index = 0x00000004, .size = sizeof(int64_t), .data = &root_ram.test_variable_i64, .name_and_description = "test_variable_i64\0A test variable of type signed 64 bit integer", .extension = NULL},
    .test_variable_u8 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT8, .flags = 0, .index = 0x00000005, .size = sizeof(uint8_t), .data = &root_ram.test_variable_u8, .name_and_description = "test_variable_u8\0A test variable of type unsigned 8 bit integer", .extension = NULL},
    .test_variable_u16 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT16, .flags = 0, .index = 0x00000006, .size = sizeof(uint16_t), .data = &root_ram.test_variable_u16, .name_and_description = "test_variable_u16\0A test variable of type unsigned 16 bit integer", .extension = NULL},
    .test_variable_u32 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT32, .flags = 0, .index = 0x00000007, .size = sizeof(uint32_t), .data = &root_ram.test_variable_u32, .name_and_description = "test_variable_u32\0A test variable of type unsigned 32 bit integer", .extension = NULL},
    .test_variable_u64 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT64, .flags = 0, .index = 0x00000008, .size = sizeof(uint64_t), .data = &root_ram.test_variable_u64, .name_and_description = "test_variable_u64\0A test variable of type unsigned 64 bit integer", .extension = NULL},
    .test_variable_float32 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_FLOAT32, .flags = 0, .index = 0x00000009, .size = sizeof(float), .data = &root_ram.test_variable_float32, .name_and_description = "test_variable_float32\0A test variable of type 32 bit floating point", .extension = NULL},
    .test_variable_float64 = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_FLOAT64, .flags = 0, .index = 0x0000000A, .size = sizeof(double), .data = &root_ram.test_variable_float64, .name_and_description = "test_variable_float64\0A test variable of type 64 bit floating point", .extension = NULL},
    .test_variable_bool_false = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_BOOL, .flags = 0, .index = 0x0000000B, .size = sizeof(bool), .data = &root_ram.test_variable_bool_false, .name_and_description = "test_variable_bool_false\0A test variable of type boolean", .extension = NULL},
    .test_variable_bool_true = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_BOOL, .flags = 0, .index = 0x0000000B, .size = sizeof(bool), .data = &root_ram.test_variable_bool_true, .name_and_description = "test_variable_bool_true\0A test variable of type boolean", .extension = NULL},
    .test_variable_char = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_CHAR, .flags = 0, .index = 0x0000000C, .size = sizeof(char), .data = &root_ram.test_variable_char, .name_and_description = "test_variable_char\0A test variable of type character", .extension = NULL},
    .group_A = {.group_A = {.other_child = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_FLOAT32, .flags = 0, .index = 0x00000031, .size = sizeof(float), .data = &root_ram.group_A.group_A.other_child, .name_and_description = "other_child\0A test variable", .extension = NULL}

                },
                .test_variable_A = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_FLOAT32, .flags = 0, .index = 0x00000011, .size = sizeof(float), .data = &root_ram.group_A.test_variable_A, .name_and_description = "test_variable_A\0A test variable", .extension = NULL},
                .test_variable_B = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_FLOAT32, .flags = 0, .index = 0x00000011, .size = sizeof(float), .data = &root_ram.group_A.test_variable_B, .name_and_description = "test_variable_B\0A test variable", .extension = NULL},
                .test_variable_small = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT8, .flags = 0, .index = 0x00000011, .size = sizeof(uint8_t), .data = &root_ram.group_A.test_variable_small, .name_and_description = "test_variable_small\0A small test variable", .extension = NULL}

    },
    .test_variable_small = {.odin_type = ODIN_TYPE_PARAMETER, .element_type = ODIN_ELEMENT_TYPE_UINT64, .flags = 0, .index = 0x00000001, .size = sizeof(uint64_t), .data = &root_ram.test_variable_small, .name_and_description = "test_variable_small\0A small test variable", .extension = NULL}};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .index = 0x00000000,
    .shift = 4,
    .count = 15,
    .parameters = {
        &root.test_variable_i8,
        &root.test_variable_i16,
        &root.test_variable_i32,
        &root.test_variable_i64,
        &root.test_variable_u8,
        &root.test_variable_u16,
        &root.test_variable_u32,
        &root.test_variable_u64,
        &root.test_variable_float32,
        &root.test_variable_float64,
        &root.test_variable_bool_false,
        &root.test_variable_bool_true,
        &root.test_variable_char,
        &odin_store_group_A,
        &root.test_variable_small,
    }};

const ODIN_parameter_group_t odin_store_group_A = {
    .name_and_description = "group_A\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .index = 0x00000010,
    .shift = 4,
    .count = 4,
    .parameters = {
        &odin_store_group_A_group_A,
        &root.group_A.test_variable_A,
        &root.group_A.test_variable_B,
        &root.group_A.test_variable_small,
    }};

const ODIN_parameter_group_t odin_store_group_A_group_A = {
    .name_and_description = "group_A\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .index = 0x00000030,
    .shift = 4,
    .count = 1,
    .parameters = {&root.group_A.group_A.other_child}};
