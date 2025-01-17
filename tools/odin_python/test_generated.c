#include <stdint.h>
#include <stdbool.h>
#include <odin.h>

typedef struct
{
    struct 
    {
        struct 
        {
            float other_child;
        }group_A;
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }group_A;
    uint64_t test_variable_small;
} root_ram_t;

typedef struct
{
    struct 
    {
        struct 
        {
            ODIN_parameter_t other_child;
        }group_A;
        ODIN_parameter_t test_variable_A;
        ODIN_parameter_t test_variable_B;
        ODIN_parameter_t test_variable_small;
    }group_A;
    ODIN_parameter_t test_variable_small;
} root_type_t;

root_ram_t root_ram = {
    .group_A = {
        .group_A = {
            .other_child = 0.0
        },
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88
    },
    .test_variable_small = 86080530548
};

const root_type_t root = {
    .group_A = {
        .group_A = {
            .other_child = {
                .odin_type = ODIN_TYPE_PARAMETER,
                .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
                .flags = 0,
                .index = 0x00000031,
                .size = sizeof(float),
                .data = &root_ram.other_child,
                .name = "other_child",
                .description = "A test variable",
                .extension = NULL
            }
        
        },
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .index = 0x00000011,
            .size = sizeof(float),
            .data = &root_ram.test_variable_A,
            .name = "test_variable_A",
            .description = "A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .index = 0x00000011,
            .size = sizeof(float),
            .data = &root_ram.test_variable_B,
            .name = "test_variable_B",
            .description = "A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = 0,
            .index = 0x00000011,
            .size = sizeof(uint8_t),
            .data = &root_ram.test_variable_small,
            .name = "test_variable_small",
            .description = "A small test variable",
            .extension = NULL
        }
    
    },
    .test_variable_small = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(uint64_t),
        .data = &root_ram.test_variable_small,
        .name = "test_variable_small",
        .description = "A small test variable",
        .extension = NULL
    }
};
