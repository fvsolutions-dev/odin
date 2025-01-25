#include "OD.h"

root_ram_t root_ram = {
    .test_variable_A = 12345,
    .basic_group = {
        .test_variable_A = 0.2,
        .test_variable_B = 1.23,
        .test_variable_small = 88
    },
    .another_group = {
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88
    }
};

const root_type_t root = {
    .test_variable_A = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0xFE000000,
        .element_size = sizeof(int32_t),
        .data = &root_ram.test_variable_A,
        .name_and_description = "test_variable_A\0A test variable",
        .extension = NULL
    },
    .basic_group = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x01010000,
            .element_size = sizeof(float),
            .data = &root_ram.basic_group.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x01020000,
            .element_size = sizeof(float),
            .data = &root_ram.basic_group.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = 0,
            .global_index = 0x01030000,
            .element_size = sizeof(uint8_t),
            .data = &root_ram.basic_group.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    },
    .another_group = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x02100000,
            .element_size = sizeof(float),
            .data = &root_ram.another_group.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x02200000,
            .element_size = sizeof(float),
            .data = &root_ram.another_group.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = 0,
            .global_index = 0x02300000,
            .element_size = sizeof(uint8_t),
            .data = &root_ram.another_group.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    }
};

const ODIN_parameter_group_t odin_store_basic_group = {
    .name_and_description = "basic_group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x01000000,
    .shift = 8,
    .count = 3,
    .parameters = {&root.basic_group.test_variable_A, &root.basic_group.test_variable_B, &root.basic_group.test_variable_small}
};

const ODIN_parameter_group_t odin_store_another_group = {
    .name_and_description = "another_group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x02000000,
    .shift = 4,
    .count = 3,
    .parameters = {&root.another_group.test_variable_A, &root.another_group.test_variable_B, &root.another_group.test_variable_small}
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 3,
    .parameters = {&root.test_variable_A, &odin_store_basic_group, &odin_store_another_group}
};
