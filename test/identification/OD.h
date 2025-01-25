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
} root_ram_t;

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
} root_type_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_group_1;
extern const ODIN_parameter_group_t odin_store_group_2_group_3;
extern const ODIN_parameter_group_t odin_store_group_2;
extern const ODIN_parameter_group_t odin_store;