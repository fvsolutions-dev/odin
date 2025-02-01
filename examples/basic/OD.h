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
} odin_variables_t;

typedef struct
{
    ODIN_parameter_t test_variable_i8;  /* Local index: 0x00000001 */
    ODIN_parameter_t test_variable_i16;  /* Local index: 0x00000002 */
    ODIN_parameter_t test_variable_i32;  /* Local index: 0x00000003 */
    ODIN_parameter_t test_variable_i64;  /* Local index: 0x00000004 */
    ODIN_parameter_t test_variable_u8;  /* Local index: 0x00000005 */
    ODIN_parameter_t test_variable_u16;  /* Local index: 0x00000006 */
    ODIN_parameter_t test_variable_u32;  /* Local index: 0x00000007 */
    ODIN_parameter_t test_variable_u64;  /* Local index: 0x00000008 */
    ODIN_parameter_t test_variable_float32;  /* Local index: 0x00000009 */
    ODIN_parameter_t test_variable_float64;  /* Local index: 0x0000000A */
    ODIN_parameter_t test_variable_bool_false;  /* Local index: 0x0000000B */
    ODIN_parameter_t test_variable_bool_true;  /* Local index: 0x0000000C */
    ODIN_parameter_t test_variable_char;  /* Local index: 0x0000000D */
    struct 
    {
        struct 
        {
            ODIN_parameter_t other_child;  /* Local index: 0x00000001 */
        }group_A;
        ODIN_parameter_t test_variable_A;  /* Local index: 0x00000002 */
        ODIN_parameter_t test_variable_B;  /* Local index: 0x00000003 */
        ODIN_parameter_t test_variable_small;  /* Local index: 0x00000005 */
    }group_A;
    ODIN_parameter_t test_variable_small;  /* Local index: 0x00000086 */
    ODIN_parameter_t u8_array;  /* Local index: 0x00000050 */
    ODIN_parameter_t u8_variable_length_array;  /* Local index: 0x00000051 */
    ODIN_parameter_t i8_array;  /* Local index: 0x00000052 */
    ODIN_parameter_t i8_variable_length_array;  /* Local index: 0x00000053 */
    ODIN_parameter_t u16_array;  /* Local index: 0x00000054 */
    ODIN_parameter_t u16_variable_length_array;  /* Local index: 0x00000055 */
    ODIN_parameter_t i16_array;  /* Local index: 0x00000056 */
    ODIN_parameter_t i16_variable_length_array;  /* Local index: 0x00000057 */
    ODIN_parameter_t u32_array;  /* Local index: 0x00000058 */
    ODIN_parameter_t u32_variable_length_array;  /* Local index: 0x00000059 */
    ODIN_parameter_t i32_array;  /* Local index: 0x0000005A */
    ODIN_parameter_t i32_variable_length_array;  /* Local index: 0x0000005B */
    ODIN_parameter_t u64_array;  /* Local index: 0x0000005C */
    ODIN_parameter_t u64_variable_length_array;  /* Local index: 0x0000005D */
    ODIN_parameter_t i64_array;  /* Local index: 0x0000005E */
    ODIN_parameter_t i64_variable_length_array;  /* Local index: 0x0000005F */
    ODIN_parameter_t float32_array;  /* Local index: 0x00000060 */
    ODIN_parameter_t float32_variable_length_array;  /* Local index: 0x00000061 */
    ODIN_parameter_t float64_array;  /* Local index: 0x00000062 */
    ODIN_parameter_t float64_variable_length_array;  /* Local index: 0x00000063 */
    ODIN_parameter_t bool_array;  /* Local index: 0x00000064 */
    ODIN_parameter_t bool_variable_length_array;  /* Local index: 0x00000065 */
    ODIN_parameter_t char_array;  /* Local index: 0x00000066 */
    ODIN_parameter_t char_variable_length_array;  /* Local index: 0x00000067 */
} odin_objects_t;

extern odin_variables_t odin_variables;
extern const odin_objects_t odin_objects;
extern const ODIN_parameter_group_t odin_store;
extern const ODIN_parameter_group_t odin_store_group_A;
extern const ODIN_parameter_group_t odin_store_group_A_group_A;