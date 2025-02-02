#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>
#include "custom_type.h"

typedef struct
{
    rgb_color_t rgb_color;
    rgb_color_t rgb_color_array[4];
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t rgb_color;  /* Local index: 0x00000001 */
    ODIN_parameter_t rgb_color_array;  /* Local index: 0x00000002 */
} odin_objects_t;

extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;

odin_variables_t odin_variables = {
    .rgb_color = {
        .r = 10,
        .g = 22,
        .b = 60
    },
    .rgb_color_array = {
        {
            .r = 10,
            .g = 22,
            .b = 60
        },{
            .r = 20,
            .g = 44,
            .b = 120
        },{
            .r = 10,
            .g = 22,
            .b = 60
        }
    }
};

const odin_objects_t odin_objects = {
    .rgb_color = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .flags = 0,
        .global_index = 0x01000000,
        .element_size = sizeof(rgb_color_t),
        .data = &odin_variables.rgb_color,
        .name_and_description = "rgb_color\0An RGB color variable",
        .extension = (ODIN_extension_t[]){ {
			.type=ODIN_EXTENSION_TYPE_STRING_CODEC,
			.ops =  &rgb_color_serialiser,
			.data = NULL,
			.next = NULL } }
    },
    .rgb_color_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .flags = 0,
        .global_index = 0x02000000,
        .element_size = sizeof(rgb_color_t),
        .data = &odin_variables.rgb_color_array,
        .name_and_description = "rgb_color_array\0An RGB color variable",
        .extension = NULL,
        .max_elements = 4
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 2,
    .parameters = {&odin_objects.rgb_color, &odin_objects.rgb_color_array}
};
