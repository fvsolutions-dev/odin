#include "OD.h"

odin_variables_t odin_variables = {
    .validate_variable = 0.2,
    .group = {
        .validate_variable = 0.2
    },
    .referenced_variable = 0,
    .referenced_variable_in_group = 0
};

const odin_objects_t odin_objects = {
    .validate_variable = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x01000000,
        .element_size = sizeof(float),
        .data = &odin_variables.validate_variable,
        .name_and_description = "validate_variable\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_VALIDATE,
			.ops =  &ODIN_validate_extension_ops,
			.data = &(range_parameter_t){ .max = 30.0, .min = -30.0 },
			.next = NULL } }
    },
    .group = {
        .validate_variable = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
            .global_index = 0x02100000,
            .element_size = sizeof(float),
            .data = &odin_variables.group.validate_variable,
            .name_and_description = "validate_variable\0A test variable",
            .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_VALIDATE,
			.ops =  &ODIN_validate_extension_ops,
			.data = &(range_parameter_t){ .max = 30.0, .min = -30.0 },
			.next = NULL } }
        }
    
    },
    .referenced_variable = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x03000000,
        .element_size = sizeof(float),
        .data = &odin_variables.referenced_variable,
        .name_and_description = "referenced_variable\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_mapped_number_ops,
			.data = &(mapped_number_parameters_t){ .reference = &odin_objects.validate_variable, .scale = 5.0, .offset = 1.0 },
			.next = NULL } }
    },
    .referenced_variable_in_group = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)),
        .global_index = 0x04000000,
        .element_size = sizeof(float),
        .data = &odin_variables.referenced_variable_in_group,
        .name_and_description = "referenced_variable_in_group\0A test variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_IO,
			.ops =  &ODIN_extension_io_mapped_number_ops,
			.data = &(mapped_number_parameters_t){ .reference = &odin_objects.group.validate_variable, .scale = 1.0, .offset = 0.0 },
			.next = NULL } }
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 4,
    .parameters = {&odin_objects.validate_variable, &odin_store_group, &odin_objects.referenced_variable, &odin_objects.referenced_variable_in_group}
};

const ODIN_parameter_group_t odin_store_group = {
    .name_and_description = "group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x02000000,
    .shift = 4,
    .count = 1,
    .parameters = {&odin_objects.group.validate_variable}
};
