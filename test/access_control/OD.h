#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
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
    struct 
    {
        ODIN_parameter_t test_variable_A;
        ODIN_parameter_t test_variable_B;
        ODIN_parameter_t test_variable_small;
    }basic_group;
    struct 
    {
        ODIN_parameter_t test_variable_A;
        ODIN_parameter_t test_variable_B;
        ODIN_parameter_t test_variable_small;
    }another_group;
} root_type_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
#define ODIN_ACCESS_CLI ODIN_ACCESS_GROUP_1
#define ODIN_ACCESS_BLE ODIN_ACCESS_GROUP_2
#define ODIN_ACCESS_GUEST ODIN_ACCESS_GROUP_3
extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_basic_group;
extern const ODIN_parameter_group_t odin_store_another_group;
extern const ODIN_parameter_group_t odin_store;