#include <stdint.h>
#include <stdbool.h>
#include <odin.h>

typedef struct
{
    float my_array[10];
    uint8_t my_array_no_default[10];
    struct 
    {
        uint16_t num_elements;
        int16_t data[50];
    }variable_length_array;
    struct 
    {
        float my_array[10];
        uint8_t my_array_no_default[10];
        struct 
        {
            uint16_t num_elements;
            int16_t data[50];
        }variable_length_array;
    }group_A;
} root_ram_t;

typedef struct
{
    ODIN_array_t my_array;
    ODIN_array_t my_array_no_default;
    ODIN_vector_t variable_length_array;
    struct 
    {
        ODIN_array_t my_array;
        ODIN_array_t my_array_no_default;
        ODIN_vector_t variable_length_array;
    }group_A;
} root_type_t;

root_ram_t root_ram = {
    .my_array = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0},
    .my_array_no_default = {0},
    .variable_length_array = {
        .data = {1, 5, 3},
        .num_elements = 3
    },
    .group_A = {
        .my_array = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0},
        .my_array_no_default = {0},
        .variable_length_array = {
            .data = {1, 5, 3},
            .num_elements = 3
        }
    
    }
};

const root_type_t root = {
    .my_array = {
        .parameter = {
            .odin_type = ODIN_TYPE_ARRAY,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .index = 0x00000001,
            .size = sizeof(float),
            .data = &root_ram.my_array,
            .name = "my_array",
            .description = "A test variable",
            .extension = NULL
        },
        .max_elements = 10
    },
    .my_array_no_default = {
        .parameter = {
            .odin_type = ODIN_TYPE_ARRAY,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = 0,
            .index = 0x00000001,
            .size = sizeof(uint8_t),
            .data = &root_ram.my_array_no_default,
            .name = "my_array_no_default",
            .description = "A test variable",
            .extension = NULL
        },
        .max_elements = 10
    },
    .variable_length_array = {
        .parameter = {
            .odin_type = ODIN_TYPE_VECTOR,
            .element_type = ODIN_ELEMENT_TYPE_INT16,
            .flags = 0,
            .index = 0x00000001,
            .size = sizeof(int16_t),
            .data = &root_ram.variable_length_array,
            .name = "variable_length_array",
            .description = "My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
            .extension = NULL
        },
        .max_elements = 50
    },
    .group_A = {
        .my_array = {
            .parameter = {
                .odin_type = ODIN_TYPE_ARRAY,
                .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
                .flags = 0,
                .index = 0x00000011,
                .size = sizeof(float),
                .data = &root_ram.my_array,
                .name = "my_array",
                .description = "A test variable",
                .extension = NULL
            },
            .max_elements = 10
        },
        .my_array_no_default = {
            .parameter = {
                .odin_type = ODIN_TYPE_ARRAY,
                .element_type = ODIN_ELEMENT_TYPE_UINT8,
                .flags = 0,
                .index = 0x00000011,
                .size = sizeof(uint8_t),
                .data = &root_ram.my_array_no_default,
                .name = "my_array_no_default",
                .description = "A test variable",
                .extension = NULL
            },
            .max_elements = 10
        },
        .variable_length_array = {
            .parameter = {
                .odin_type = ODIN_TYPE_VECTOR,
                .element_type = ODIN_ELEMENT_TYPE_INT16,
                .flags = 0,
                .index = 0x00000011,
                .size = sizeof(int16_t),
                .data = &root_ram.variable_length_array,
                .name = "variable_length_array",
                .description = "My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
                .extension = NULL
            },
            .max_elements = 50
        }
    
    }
};
