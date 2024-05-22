#include <stdint.h>
#include "odin_datastore.h"

#define ODIN_ACCESS_INTERNAL (1<<4)
#define ODIN_ACCESS_TYPE_INTERNAL_READ (ODIN_ACCESS_INTERNAL << ODIN_READ_ACCESS)
#define ODIN_ACCESS_TYPE_INTERNAL_WRITE (ODIN_ACCESS_INTERNAL << ODIN_WRITE_ACCESS)

#define ODIN_ACCESS_OTHER (1<<6)
#define ODIN_ACCESS_TYPE_OTHER_READ (ODIN_ACCESS_OTHER << ODIN_READ_ACCESS)
#define ODIN_ACCESS_TYPE_OTHER_WRITE (ODIN_ACCESS_OTHER << ODIN_WRITE_ACCESS)

typedef struct
{
    struct 
    {
        uint16_t variable;
    }test_data;
} ODIN_ram_t;

typedef struct
{
    struct 
    {
        ODIN_parameter_t variable;
    }test_data;
} ODIN_params_t;

extern ODIN_ram_t ODIN_ram; /* Value storage for the ODIN RAM data store. */
extern ODIN_params_t ODIN_params;
extern ODIN_parameter_group_t ODIN_datastore_test_data;
extern ODIN_store_t ODIN_datastore;