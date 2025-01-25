#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    int32_t test_variable_i32;
    int32_t i32_array[10];
    struct 
    {
        size_t num_elements;
        int32_t data[50];
    }i32_variable_length_array;
} root_ram_t;

typedef struct
{
    ODIN_parameter_t test_variable_i32;  /* Local index: 0x00000001 */
    ODIN_parameter_t i32_array;  /* Local index: 0x00000002 */
    ODIN_parameter_t i32_variable_length_array;  /* Local index: 0x00000003 */
} root_type_t;

extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store;