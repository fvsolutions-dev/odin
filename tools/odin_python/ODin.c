#include <stdint.h>
#include "odin_datastore.h"
#include "ODin.h"

ODIN_ram_t ODIN_ram = {
    .test_data = {
        .variable = 0
    }
};

ODIN_params_t ODIN_params = {
    .test_data = {
        .variable = {
            .index = 0xa0001,
            .access = ODIN_ACCESS_TYPE_INTERNAL_READ|ODIN_ACCESS_TYPE_INTERNAL_WRITE|ODIN_ACCESS_TYPE_OTHER_READ|ODIN_ACCESS_TYPE_OTHER_WRITE,
            .format = ODIN_ENCODING_NUMBER,
            .type = ODIN_ELEMENT_TYPE_UINT16,
            .data = &ODIN_ram.test_data.variable,
            .size = sizeof(uint16_t),
            .name = "variable",
            .description = "something\n"
        }
    
    }
};

ODIN_parameter_group_t ODIN_datastore_test_data = {
    .name = "test_data",
    .description = "Group description\n",
    .index = 0xa,
    .count = 1,
    .parameters = {&ODIN_params.test_data.variable}
};

ODIN_store_t ODIN_datastore = {
    .count = 1,
    .groups = {&ODIN_datastore_test_data}
};