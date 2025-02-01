#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    float validate_variable;
    struct 
    {
        float validate_variable;
    }group;
    float referenced_variable;
    float referenced_variable_in_group;
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t validate_variable;  /* Local index: 0x00000001 */
    struct 
    {
        ODIN_parameter_t validate_variable;  /* Local index: 0x00000001 */
    }group;
    ODIN_parameter_t referenced_variable;  /* Local index: 0x00000003 */
    ODIN_parameter_t referenced_variable_in_group;  /* Local index: 0x00000004 */
} odin_objects_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group;