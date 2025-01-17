#include <stddef.h>


typedef enum {
    ODIN_TYPE_PARAMETER = 0,
    ODIN_TYPE_ARRAY = 1,
    ODIN_TYPE_VECTOR = 2,
} ODIN_type_t;

typedef enum {
    ODIN_ELEMENT_TYPE_BOOL = 0,
    ODIN_ELEMENT_TYPE_HEX = 1,
    ODIN_ELEMENT_TYPE_UINT8 = 2,
    ODIN_ELEMENT_TYPE_UINT16 = 3,
    ODIN_ELEMENT_TYPE_UINT32 = 4,
    ODIN_ELEMENT_TYPE_UINT64 = 5,
    ODIN_ELEMENT_TYPE_INT8 = 6,
    ODIN_ELEMENT_TYPE_INT16 = 7,
    ODIN_ELEMENT_TYPE_INT32 = 8,
    ODIN_ELEMENT_TYPE_INT64 = 9,
    ODIN_ELEMENT_TYPE_FLOAT32 = 10,
    ODIN_ELEMENT_TYPE_FLOAT64 = 11,
    ODIN_ELEMENT_TYPE_CHAR = 12,
    ODIN_ELEMENT_TYPE_CUSTOM = 13,
} ODIN_element_type_t;


typedef struct
{
    ODIN_type_t odin_type;
    ODIN_element_type_t element_type;
    uint32_t flags;
    uint32_t index;
    size_t size;
    void *data;
    const char *name;
    const char *description;
    void *extension;
} ODIN_parameter_t;

