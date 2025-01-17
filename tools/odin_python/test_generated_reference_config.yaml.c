#include <stdint.h>
#include <stdbool.h>
#include <odin.h>

typedef struct
{
} root_ram_t;

typedef struct
{
    ODIN_parameter_t test_variable_A;
    ODIN_parameter_t test_variable_testy;
} root_type_t;

root_ram_t root_ram = {
};

const root_type_t root = {
    .test_variable_A = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(float),
        .data = &my.reference,
        .name = "test_variable_A",
        .description = "A test variable",
        .extension = NULL
    },
    .test_variable_testy = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .index = 0x00000001,
        .size = sizeof(uint64_t),
        .data = &current_time_in_microseconds,
        .name = "test_variable_testy",
        .description = "A test variable",
        .extension = NULL
    }
};
