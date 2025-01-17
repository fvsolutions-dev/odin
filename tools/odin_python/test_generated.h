#include <stdint.h>
#include <stdbool.h>
#include <odin.h>

typedef struct
{
    struct 
    {
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }group_A;
    uint64_t test_variable_small;
} root_ram_t;

typedef struct
{
    struct 
    {
        ODIN_parameter_t test_variable_A;
        ODIN_parameter_t test_variable_B;
        ODIN_parameter_t test_variable_small;
    }group_A;
    ODIN_parameter_t test_variable_small;
} root_type_t;
