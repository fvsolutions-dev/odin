#include <stdint.h>
#include <stdbool.h>
#include <odin.h>
#include <odin_security.h>

typedef struct
{
    struct 
    {
        float test_variable_A;
    }another_group;
} root_ram_t;

typedef struct
{
    struct 
    {
        ODIN_parameter_t test_variable_A;
    }another_group;
} root_type_t;

#define ODIN_ACCESS_DISK ODIN_ACCESS_GROUP_0
#define ODIN_ACCESS_CLI ODIN_ACCESS_GROUP_1
#define ODIN_ACCESS_BLE ODIN_ACCESS_GROUP_2
#define ODIN_ACCESS_GUEST ODIN_ACCESS_GROUP_3
extern root_ram_t root_ram;
extern const root_type_t root;
extern const ODIN_parameter_group_t odin_store_another_group;
extern const ODIN_parameter_group_t odin_store;

root_ram_t root_ram = {
    .another_group = {
        .test_variable_A = 0.0
    }
};

const root_type_t root = {
    .another_group = {
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = (ODIN_ACCESS_DISK & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_CLI & (ODIN_ACCESS_READ | ODIN_ACCESS_LOG_WRITE)),
            .index = 0x00000003,
            .element_size = sizeof(float),
            .data = &root_ram.another_group.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        }
    
    }
};

const ODIN_parameter_group_t odin_store_another_group = {
    .name_and_description = "another_group\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .index = 0x00000002,
    .shift = 4,
    .count = 1,
    .parameters = {&root.another_group.test_variable_A}
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .index = 0x00000000,
    .shift = 4,
    .count = 1,
    .parameters = {&odin_store_another_group}
};
