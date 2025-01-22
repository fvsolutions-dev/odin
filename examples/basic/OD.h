#include <stdint.h>
#include <stdbool.h>
#include <odin.h>

typedef struct
{
    int8_t test_variable_i8;
    int16_t test_variable_i16;
    int32_t test_variable_i32;
    int64_t test_variable_i64;
    uint8_t test_variable_u8;
    uint16_t test_variable_u16;
    uint32_t test_variable_u32;
    uint64_t test_variable_u64;
    float test_variable_float32;
    double test_variable_float64;
    bool test_variable_bool_false;
    bool test_variable_bool_true;
    char test_variable_char;
    struct 
    {
        struct 
        {
            float other_child;
        }group_A;
        float test_variable_A;
        float test_variable_B;
        uint8_t test_variable_small;
    }group_A;
    uint64_t test_variable_small;
} root_ram_t;

typedef struct
{
    ODIN_parameter_t test_variable_i8;
    ODIN_parameter_t test_variable_i16;
    ODIN_parameter_t test_variable_i32;
    ODIN_parameter_t test_variable_i64;
    ODIN_parameter_t test_variable_u8;
    ODIN_parameter_t test_variable_u16;
    ODIN_parameter_t test_variable_u32;
    ODIN_parameter_t test_variable_u64;
    ODIN_parameter_t test_variable_float32;
    ODIN_parameter_t test_variable_float64;
    ODIN_parameter_t test_variable_bool_false;
    ODIN_parameter_t test_variable_bool_true;
    ODIN_parameter_t test_variable_char;
    struct 
    {
        struct 
        {
            ODIN_parameter_t other_child;
        }group_A;
        ODIN_parameter_t test_variable_A;
        ODIN_parameter_t test_variable_B;
        ODIN_parameter_t test_variable_small;
    }group_A;
    ODIN_parameter_t test_variable_small;
} root_type_t;

extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group_A;
extern const ODIN_parameter_group_t odin_store_group_A_group_A;