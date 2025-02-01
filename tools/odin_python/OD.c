#include "OD.h"

root_ram_t odin_variables = {
    .test_variable_A = 0.0,
    .test_variable_B = 1.23,
    .test_variable_small = 88
};

const root_type_t root = {
    .test_variable_A = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(float),
        .data = &odin_variables.test_variable_A,
        .name_and_description = "test_variable_A\0A test variable",
        .extension = NULL
    },
    .test_variable_B = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(float),
        .data = &odin_variables.test_variable_B,
        .name_and_description = "test_variable_B\0A test variable",
        .extension = NULL
    },
    .test_variable_small = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT8,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(uint8_t),
        .data = &odin_variables.test_variable_small,
        .name_and_description = "test_variable_small\0A small test variable",
        .extension = NULL
    }
};
