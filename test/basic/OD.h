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
    int32_t i32_array[10];
    struct 
    {
        size_t num_elements;
        int32_t data[50];
    }i32_variable_length_array;
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
    ODIN_parameter_t i32_array;
    ODIN_parameter_t i32_variable_length_array;
} root_type_t;

extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store;