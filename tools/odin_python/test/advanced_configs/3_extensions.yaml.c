#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    float base_variable_float;
    struct 
    {
        float base_variable_group;
    }group;
    float base_variable_reference_extension;
    float base_variable_reference_group_extension;
} root_ram_t;

typedef struct
{
    ODIN_parameter_t base_variable_float;  /* Local index: 0x00000001 */
    struct 
    {
        ODIN_parameter_t base_variable_group;  /* Local index: 0x00000001 */
    }group;
    ODIN_parameter_t base_variable_reference_extension;  /* Local index: 0x00000003 */
    ODIN_parameter_t base_variable_reference_group_extension;  /* Local index: 0x00000004 */
} root_type_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_group;
extern const ODIN_parameter_group_t odin_store;

root_ram_t root_ram = {
    .base_variable_float = 0.2,
    .group = {
        .base_variable_group = 0.2
    },
    .base_variable_reference_extension = 0,
    .base_variable_reference_group_extension = 0
};

const root_type_t root = {
    .base_variable_float = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x01000000,
        .element_size = sizeof(float),
        .data = &root_ram.base_variable_float,
        .name_and_description = "base_variable_float\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_validate_extension_ops,
			.data = &(range_parameter_t){ .max = 30.0, .min = -30.0 },
			.next = NULL } }
    },
    .group = {
        .base_variable_group = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
            .global_index = 0x02100000,
            .element_size = sizeof(float),
            .data = &root_ram.group.base_variable_group,
            .name_and_description = "base_variable_group\0A test variable",
            .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_validate_extension_ops,
			.data = &(range_parameter_t){ .max = 30.0, .min = -30.0 },
			.next = NULL } }
        }
    
    },
    .base_variable_reference_extension = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x03000000,
        .element_size = sizeof(float),
        .data = &root_ram.base_variable_reference_extension,
        .name_and_description = "base_variable_reference_extension\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_reference_ops,
			.data = &(reference_parameters_t){ .reference = &root.base_variable_float},
			.next = NULL } }
    },
    .base_variable_reference_group_extension = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x04000000,
        .element_size = sizeof(float),
        .data = &root_ram.base_variable_reference_group_extension,
        .name_and_description = "base_variable_reference_group_extension\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_reference_ops,
			.data = &(reference_parameters_t){ .reference = &root.group.base_variable_float},
			.next = NULL } }
    }
};

const ODIN_parameter_group_t odin_store_group = {
    .name_and_description = "group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x02000000,
    .shift = 4,
    .count = 1,
    .parameters = {&root.group.base_variable_group}
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 4,
    .parameters = {&root.base_variable_float, &odin_store_group, &root.base_variable_reference_extension, &root.base_variable_reference_group_extension}
};
