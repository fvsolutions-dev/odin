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