#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    float test_variable_A;
    float test_variable_B;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }group_1;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
        struct 
        {
            float test_variable_A;
            float test_variable_B;
            uint8_t test_variable_small;
        }group_3;
    }group_2;
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
    ODIN_parameter_t test_variable_B;  /* Local index: 0x000000FF */
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
    }group_1;
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
        struct 
        {
            ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
            ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
            ODIN_parameter_t test_variable_small;  /* Local index: 0x000005FF */
        }group_3;
    }group_2;
} odin_objects_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group_1;
extern const ODIN_parameter_group_t odin_store_group_2;
extern const ODIN_parameter_group_t odin_store_group_2_group_3;

odin_variables_t odin_variables = {
    .test_variable_A = 0.2,
    .test_variable_B = 1.23,
    .group_1 = {
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88
    },
    .group_2 = {
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88,
        .group_3 = {
            .test_variable_A = 0.0,
            .test_variable_B = 1.23,
            .test_variable_small = 88
        }
    
    }
};

const odin_objects_t odin_objects = {
    .test_variable_A = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
        .global_index = 0x01000000,
        .element_size = sizeof(float),
        .data = &odin_variables.test_variable_A,
        .name_and_description = "test_variable_A\0A test variable",
        .extension = NULL
    },
    .test_variable_B = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
        .global_index = 0xFF000000,
        .element_size = sizeof(float),
        .data = &odin_variables.test_variable_B,
        .name_and_description = "test_variable_B\0A test variable",
        .extension = NULL
    },
    .group_1 = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x03010000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_1.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x03020000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_1.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x03030000,
            .element_size = sizeof(uint8_t),
            .data = &odin_variables.group_1.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    },
    .group_2 = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x04100000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_2.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x04200000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_2.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
            .global_index = 0x04300000,
            .element_size = sizeof(uint8_t),
            .data = &odin_variables.group_2.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        },
        .group_3 = {
            .test_variable_A = {
                .odin_type = ODIN_TYPE_PARAMETER,
                .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
                .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
                .global_index = 0x04400100,
                .element_size = sizeof(float),
                .data = &odin_variables.group_2.group_3.test_variable_A,
                .name_and_description = "test_variable_A\0A test variable",
                .extension = NULL
            },
            .test_variable_B = {
                .odin_type = ODIN_TYPE_PARAMETER,
                .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
                .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
                .global_index = 0x04400200,
                .element_size = sizeof(float),
                .data = &odin_variables.group_2.group_3.test_variable_B,
                .name_and_description = "test_variable_B\0A test variable",
                .extension = NULL
            },
            .test_variable_small = {
                .odin_type = ODIN_TYPE_PARAMETER,
                .element_type = ODIN_ELEMENT_TYPE_UINT8,
                .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
                .global_index = 0x0445FF00,
                .element_size = sizeof(uint8_t),
                .data = &odin_variables.group_2.group_3.test_variable_small,
                .name_and_description = "test_variable_small\0A small test variable",
                .extension = NULL
            }
        
        }
    
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 4,
    .parameters = {&odin_objects.test_variable_A, &odin_objects.test_variable_B, &odin_store_group_1, &odin_store_group_2}
};

const ODIN_parameter_group_t odin_store_group_1 = {
    .name_and_description = "group_1\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x03000000,
    .shift = 8,
    .count = 3,
    .parameters = {&odin_objects.group_1.test_variable_A, &odin_objects.group_1.test_variable_B, &odin_objects.group_1.test_variable_small}
};

const ODIN_parameter_group_t odin_store_group_2 = {
    .name_and_description = "group_2\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x04000000,
    .shift = 4,
    .count = 4,
    .parameters = {&odin_objects.group_2.test_variable_A, &odin_objects.group_2.test_variable_B, &odin_objects.group_2.test_variable_small, &odin_store_group_2_group_3}
};

const ODIN_parameter_group_t odin_store_group_2_group_3 = {
    .name_and_description = "group_3\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x04400000,
    .shift = 12,
    .count = 3,
    .parameters = {&odin_objects.group_2.group_3.test_variable_A, &odin_objects.group_2.group_3.test_variable_B, &odin_objects.group_2.group_3.test_variable_small}
};
