#include "OD.h"

odin_variables_t odin_variables = {
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

const odin_objects_t odin_objects = {
    .basic_group = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)) | (ODIN_ACCESS_BLE & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
            .global_index = 0x01010000,
            .element_size = sizeof(float),
            .data = &odin_variables.basic_group.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_BLE & (ODIN_ACCESS_READ)) | (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)),
            .global_index = 0x01020000,
            .element_size = sizeof(float),
            .data = &odin_variables.basic_group.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)) | (ODIN_ACCESS_BLE & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
            .global_index = 0x01030000,
            .element_size = sizeof(uint8_t),
            .data = &odin_variables.basic_group.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    },
    .another_group = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)),
            .global_index = 0x02100000,
            .element_size = sizeof(float),
            .data = &odin_variables.another_group.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)),
            .global_index = 0x02200000,
            .element_size = sizeof(float),
            .data = &odin_variables.another_group.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)),
            .global_index = 0x02300000,
            .element_size = sizeof(uint8_t),
            .data = &odin_variables.another_group.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 2,
    .parameters = {&odin_store_basic_group, &odin_store_another_group}
};

const ODIN_parameter_group_t odin_store_basic_group = {
    .name_and_description = "basic_group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x01000000,
    .shift = 8,
    .count = 3,
    .parameters = {&odin_objects.basic_group.test_variable_A, &odin_objects.basic_group.test_variable_B, &odin_objects.basic_group.test_variable_small}
};

const ODIN_parameter_group_t odin_store_another_group = {
    .name_and_description = "another_group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x02000000,
    .shift = 4,
    .count = 3,
    .parameters = {&odin_objects.another_group.test_variable_A, &odin_objects.another_group.test_variable_B, &odin_objects.another_group.test_variable_small}
};
