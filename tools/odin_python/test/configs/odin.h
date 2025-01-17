#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

extern uint64_t current_time_in_microseconds;
struct my_struct
{
    float reference;
};

extern struct my_struct my;

typedef enum
{
    ODIN_TYPE_PARAMETER, // Single value
    ODIN_TYPE_ARRAY,     // Fixed length array
    ODIN_TYPE_VECTOR     // Variable length array, with a maximum length, keeps track of the current length
} ODIN_type_t;

typedef enum
{
    ODIN_ELEMENT_TYPE_BOOL,

    ODIN_ELEMENT_TYPE_HEX, // Same UINT8, but will be displayed as hex

    ODIN_ELEMENT_TYPE_UINT8,
    ODIN_ELEMENT_TYPE_UINT16,
    ODIN_ELEMENT_TYPE_UINT32,
    ODIN_ELEMENT_TYPE_UINT64,

    ODIN_ELEMENT_TYPE_INT8,
    ODIN_ELEMENT_TYPE_INT16,
    ODIN_ELEMENT_TYPE_INT32,
    ODIN_ELEMENT_TYPE_INT64,

    ODIN_ELEMENT_TYPE_FLOAT32,
    ODIN_ELEMENT_TYPE_FLOAT64,

    ODIN_ELEMENT_TYPE_CHAR,
    ODIN_ELEMENT_TYPE_CUSTOM // Custom data type, custom to string and validator functions have to be provided
} ODIN_element_type_t;

typedef enum
{
    ODIN_EXTENSION_TYPE_STRING,
    ODIN_EXTENSION_TYPE_IO,
    ODIN_EXTENSION_TYPE_VALIDATE,
} ODIN_extension_type_t;


// Extension definition
struct ODIN_extension;

typedef struct ODIN_extension
{
    ODIN_extension_type_t type; // Type of the extension
    void *ops;                  // Operations for the extension, check the type to cast to the correct type
    void *data;                 // Metadata for the extension, can be NULL
    struct ODIN_extension *next;     // Next extension in the list, can be NULL
} ODIN_extension_t;

#define ODIN_INCLUDE_NAME
#define ODIN_INCLUDE_DESCRIPTION

typedef struct
{
    // Type of the parameter
    ODIN_type_t odin_type : 4;

    // Type of the element
    ODIN_element_type_t element_type : 8;

    uint16_t flags;

    // Index (ID) of the parameter
    uint16_t index;

    // Size of the data
    uint16_t size;

    // Pointer to the data
    void *data;

    // Name of the parameter
#ifdef ODIN_INCLUDE_NAME
    const char *name;
#endif

#ifdef ODIN_INCLUDE_DESCRIPTION
    const char *description;
#endif

    // Extension info
    const ODIN_extension_t *extension; // Linked list of extensions, can be NULL

} ODIN_parameter_t;

typedef struct
{
    ODIN_parameter_t parameter;
    uint16_t max_elements;
} ODIN_array_t;

typedef struct
{
    ODIN_parameter_t parameter;
    uint16_t max_elements;
} ODIN_vector_t;


// String serialisation extension type
typedef struct
{
    // Represents data as a string
    int (*to_string)(const ODIN_parameter_t *parameter, const void *data, size_t size, char *buffer, size_t buffer_size);

    // Parses string into data
    int (*from_string)(const ODIN_parameter_t *parameter, const char *string, void *data, size_t size);
} ODIN_string_serialisation_extension_ops_t;

// IO extension type
typedef struct
{
    // Write data to the parameter
    int (*write)(const ODIN_parameter_t *parameter, const void *data, size_t size, uint16_t access_group);

    // Read data from the parameter
    int (*read)(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
} ODIN_io_extension_ops_t;

typedef struct
{
    // Validates the data
    int (*validate)(const ODIN_parameter_t *parameter, const void *data, size_t size, uint16_t access_group);

} ODIN_validate_extension_ops_t;
