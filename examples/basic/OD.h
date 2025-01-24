#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

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
    uint8_t u8_array[10];
    struct 
    {
        size_t num_elements;
        uint8_t data[50];
    }u8_variable_length_array;
    int8_t i8_array[10];
    struct 
    {
        size_t num_elements;
        int8_t data[50];
    }i8_variable_length_array;
    uint16_t u16_array[10];
    struct 
    {
        size_t num_elements;
        uint16_t data[50];
    }u16_variable_length_array;
    int16_t i16_array[10];
    struct 
    {
        size_t num_elements;
        int16_t data[50];
    }i16_variable_length_array;
    uint32_t u32_array[10];
    struct 
    {
        size_t num_elements;
        uint32_t data[50];
    }u32_variable_length_array;
    int32_t i32_array[10];
    struct 
    {
        size_t num_elements;
        int32_t data[50];
    }i32_variable_length_array;
    uint64_t u64_array[10];
    struct 
    {
        size_t num_elements;
        uint64_t data[50];
    }u64_variable_length_array;
    int64_t i64_array[10];
    struct 
    {
        size_t num_elements;
        int64_t data[50];
    }i64_variable_length_array;
    float float32_array[10];
    struct 
    {
        size_t num_elements;
        float data[50];
    }float32_variable_length_array;
    double float64_array[10];
    struct 
    {
        size_t num_elements;
        double data[50];
    }float64_variable_length_array;
    bool bool_array[10];
    struct 
    {
        size_t num_elements;
        bool data[50];
    }bool_variable_length_array;
    char char_array[10];
    struct 
    {
        size_t num_elements;
        char data[50];
    }char_variable_length_array;
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
    ODIN_parameter_t u8_array;
    ODIN_parameter_t u8_variable_length_array;
    ODIN_parameter_t i8_array;
    ODIN_parameter_t i8_variable_length_array;
    ODIN_parameter_t u16_array;
    ODIN_parameter_t u16_variable_length_array;
    ODIN_parameter_t i16_array;
    ODIN_parameter_t i16_variable_length_array;
    ODIN_parameter_t u32_array;
    ODIN_parameter_t u32_variable_length_array;
    ODIN_parameter_t i32_array;
    ODIN_parameter_t i32_variable_length_array;
    ODIN_parameter_t u64_array;
    ODIN_parameter_t u64_variable_length_array;
    ODIN_parameter_t i64_array;
    ODIN_parameter_t i64_variable_length_array;
    ODIN_parameter_t float32_array;
    ODIN_parameter_t float32_variable_length_array;
    ODIN_parameter_t float64_array;
    ODIN_parameter_t float64_variable_length_array;
    ODIN_parameter_t bool_array;
    ODIN_parameter_t bool_variable_length_array;
    ODIN_parameter_t char_array;
    ODIN_parameter_t char_variable_length_array;
} root_type_t;

extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_group_A_group_A;
extern const ODIN_parameter_group_t odin_store_group_A;
extern const ODIN_parameter_group_t odin_store;