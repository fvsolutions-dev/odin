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