#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>


#pragma once

// Temp references
extern uint64_t current_time_in_microseconds;
struct my_struct {
    float reference;
};

extern struct my_struct my;
#define LOG_ERR(tag, format, ...) printf(format "\n", ##__VA_ARGS__)



typedef enum {
    ODIN_SUCCESS = 0,
    ODIN_ERROR = -20,
    ODIN_ERROR_NO_PARAMETER = -1,
    ODIN_ERROR_INVALID_ARGUMENT = -100,
    ODIN_ERROR_PARAMETER_NOT_FOUND = -6,
    ODIN_ERROR_SIZE_MISMATCH = -2,
    ODIN_ERROR_PERMISSION_DENIED = -3,
    ODIN_ERROR_UNSUPPORTED_FORMAT = -4,
    ODIN_ERROR_NOT_SUPPORTED = -5,
    ODIN_ERR_FILE_NOT_FOUND = -7
} odin_error_t;


typedef enum {
    ODIN_TYPE_PARAMETER,  // Single value
    ODIN_TYPE_ARRAY,      // Fixed length array
    ODIN_TYPE_VECTOR,     // Preallocated variable length array (keeps track of the
                          // current length, with a separate pointer)
    ODIN_TYPE_GROUP       // Group of parameters
} ODIN_type_t;

typedef enum {
    ODIN_ELEMENT_TYPE_BOOL,

    ODIN_ELEMENT_TYPE_HEX,  // Same UINT8, but will be displayed as hex

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
    ODIN_ELEMENT_TYPE_CUSTOM  // Custom data type, custom to string and validator
                              // functions have to be provided
} ODIN_element_type_t;

typedef enum {
    ODIN_EXTENSION_TYPE_STRING,
    ODIN_EXTENSION_TYPE_IO,
    ODIN_EXTENSION_TYPE_VALIDATE,
} ODIN_extension_type_t;

// Extension definition
struct ODIN_extension;

typedef struct ODIN_extension {
    ODIN_extension_type_t type;   // Type of the extension
    void *ops;                    // Operations for the extension, check the type to cast to the
                                  // correct type
    void *data;                   // Metadata for the extension, can be NULL
    struct ODIN_extension *next;  // Next extension in the list, can be NULL
} ODIN_extension_t;

#define ODIN_INCLUDE_NAME
#define ODIN_INCLUDE_DESCRIPTION

typedef struct {
    size_t num_elements;
    uint8_t data[2];  // Not a pointer, but a array
} ODIN_vector_structure_t;

#pragma pack(push, 1)
typedef struct {
    // Type of the parameter
    ODIN_type_t odin_type : 8;

    // Type of the element
    ODIN_element_type_t element_type : 8;

    // Extra flags
    uint16_t flags;

    // Index (ID) of the parameter
    uint16_t index;

    // Size of a single element
    uint16_t element_size;

    // Max elements for arrays and vectors, otherwise 1
    uint16_t max_elements;

    // Pointer to the data
    void *data;

    // Name of the parameter, double null terminated, the first null is the end of
    // the string, the second null is the end of description
#ifdef ODIN_INCLUDE_NAME
    const char *name_and_description;
#endif

    // Extension info
    const ODIN_extension_t *extension;  // Linked list of extensions, can be NULL

} ODIN_parameter_t;
#pragma pack(pop)

// String serialisation extension type
typedef struct {
    // Represents data as a string
    int (*to_string)(const ODIN_parameter_t *parameter, const void *data, size_t size, char *buffer,
                     size_t buffer_size);

    // Parses string into data
    int (*from_string)(const ODIN_parameter_t *parameter, const char *string, void *data, size_t size);
} ODIN_string_serialisation_extension_ops_t;

// IO extension type
typedef struct {
    // Write data to the parameter
    int (*write)(const ODIN_parameter_t *parameter, const void *data, size_t size, uint16_t access_group);

    // Read data from the parameter
    int (*read)(const ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
} ODIN_io_extension_ops_t;

typedef struct {
    // Validates the data
    int (*validate)(const ODIN_parameter_t *parameter, const void *data, size_t size, uint16_t access_group);

} ODIN_validate_extension_ops_t;

typedef struct {
    ODIN_type_t odin_type : 4;
} ODIN_parameter_generic_t;

typedef struct {
    ODIN_type_t odin_type : 4;
    uint16_t index;  // Bits to shift to get the index
    uint16_t shift;  // Bits to shift to get the index
    uint16_t type;   // Number of parameters in the group
    uint16_t count;  // Number of parameters in the group

    const char *name_and_description;
    const void *parameters[];
} ODIN_parameter_group_t;

// A return eatly macro if not successful, which only executes the code once
#define RETURN_ON_FAIL(x) \
    do {                               \
        int ret = (x);                 \
        if (ret < 0) {                 \
            return ret;                \
        }                              \
    } while (0)


