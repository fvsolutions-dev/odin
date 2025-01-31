#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    float base_variable_float;
} root_ram_t;

typedef struct
{
    ODIN_parameter_t base_variable_float;  /* Local index: 0x00000001 */
} root_type_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store;

root_ram_t root_ram = {
    .base_variable_float = 0.2
};

const root_type_t root = {
    .base_variable_float = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_WRITE | ODIN_ACCESS_READ)),
        .global_index = 0x01000000,
        .element_size = sizeof(float),
        .data = &root_ram.base_variable_float,
        .name_and_description = "base_variable_float\0A test variable",
        .extension = NULL
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 1,
    .parameters = {&root.base_variable_float}
};
