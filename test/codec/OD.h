#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    int32_t test_variable_A;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }basic_group;
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }another_group;
} root_ram_t;

typedef struct
{
    ODIN_parameter_t test_variable_A;  /* Local index: 0x000000FE */
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
    }basic_group;
    struct 
    {
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000001 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000003 */
    }another_group;
} root_type_t;

extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_basic_group;
extern const ODIN_parameter_group_t odin_store_another_group;
extern const ODIN_parameter_group_t odin_store;