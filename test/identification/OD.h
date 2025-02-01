#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    float test_variable_A;
    float test_variable_B;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }group_1;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
        struct 
        {
            float test_variable_A;
            float test_variable_B;
            uint8_t test_variable_small;
        }group_3;
    }group_2;
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
    ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
    }group_1;
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
        struct 
        {
            ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
            ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
            ODIN_parameter_t test_variable_small;  /* Local index: 0x000005FF */
        }group_3;
    }group_2;
} odin_objects_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group_1;
extern const ODIN_parameter_group_t odin_store_group_2;
extern const ODIN_parameter_group_t odin_store_group_2_group_3;