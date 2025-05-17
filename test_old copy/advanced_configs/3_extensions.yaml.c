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
    int32_t base_variable_reference_group_extension;
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t base_variable_float;  /* Local index: 0x00000001 */
    struct 
    {
        ODIN_parameter_t base_variable_group;  /* Local index: 0x00000001 */
    }group;
    ODIN_parameter_t base_variable_reference_extension;  /* Local index: 0x00000003 */
    ODIN_parameter_t base_variable_reference_group_extension;  /* Local index: 0x00000004 */
} odin_objects_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group;

odin_variables_t odin_variables = {
    .base_variable_float = 0.2,
    .group = {
        .base_variable_group = 0.2
    },
    .base_variable_reference_extension = 0,
    .base_variable_reference_group_extension = 0
};

const odin_objects_t odin_objects = {
    .base_variable_float = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x01000000,
        .element_size = sizeof(float),
        .data = &odin_variables.base_variable_float,
        .name_and_description = "base_variable_float\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_VALIDATE,
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
            .data = &odin_variables.group.base_variable_group,
            .name_and_description = "base_variable_group\0A test variable",
            .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_VALIDATE,
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
        .data = &odin_variables.base_variable_reference_extension,
        .name_and_description = "base_variable_reference_extension\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_mapped_number_ops,
			.data = &(mapped_number_parameters_t){ .reference = &odin_objects.base_variable_float, .scale = 1.0, .offset = 0.0 },
			.next = NULL } }
    },
    .base_variable_reference_group_extension = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x04000000,
        .element_size = sizeof(int32_t),
        .data = &odin_variables.base_variable_reference_group_extension,
        .name_and_description = "base_variable_reference_group_extension\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_mapped_number_ops,
			.data = &(mapped_number_parameters_t){ .reference = &odin_objects.group.base_variable_group, .scale = 1.0, .offset = 0.0 },
			.next = NULL } }
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 4,
    .parameters = {&odin_objects.base_variable_float, &odin_store_group, &odin_objects.base_variable_reference_extension, &odin_objects.base_variable_reference_group_extension}
};

const ODIN_parameter_group_t odin_store_group = {
    .name_and_description = "group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x02000000,
    .shift = 4,
    .count = 1,
    .parameters = {&odin_objects.group.base_variable_group}
};
