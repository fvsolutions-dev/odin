#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "odin/extensions.h"
#ifndef ODIN_H
#define ODIN_H

/**
 * @brief Enum for the different encoding formats
 * It defines the way the data is printed and parsed to
 */
enum ODIN_string_encoding_format_t
{
    ODIN_ENCODING_NONE,        // Encoding not defined
    ODIN_ENCODING_UINT,        // Encoding as unsigned integer (up to 32 bits number)
    ODIN_ENCODING_INT,         // Encoding as signed integer (up to 32 bits number)
    ODIN_ENCODING_HEX,         // Encoding as hexadecimal (any length)
    ODIN_ENCODING_HEX_LSB,     // Encoding as hexadecimal with least significant byte first (any length)
    ODIN_ENCODING_HEX_MSB,     // Encoding as hexadecimal with most significant byte first (any length)
    ODIN_ENCODING_FLOAT,       // Encoding as float (32 bits)
    ODIN_ENCODING_UTF8,        // Encoding as UTF8 string (any length), automatically null terminated if its not
    ODIN_ENCODING_UINT8_ARRAY, // Encoding as array of unsigned 8 bit integers (any length)
};


enum ODIN_element_type_t
{
    ODIN_ELEMENT_TYPE_FLOAT,
    ODIN_ELEMENT_TYPE_BOOL,
    ODIN_ELEMENT_TYPE_INT,
    ODIN_ELEMENT_TYPE_UINT,
    ODIN_ELEMENT_TYPE_BLOB,
    ODIN_ELEMENT_TYPE_OTHER
};




typedef struct ODIN_parameter_t
{
    const uint32_t index;                            // Full index of parameter
    const uint16_t access;                           // 2 bytes
    void *data;                                // pointer to data
    const uint16_t size;                             // size of data
    const enum ODIN_element_type_t type;             // type of data
    const enum ODIN_string_encoding_format_t format; // formater of data used to serialize and deserialize to string
    const char *description;                         // description of data, can be NULL
    const char *name;                                // name of data
    ODIN_extension_t *extension;                     // extension info, can be NULL
} ODIN_parameter_t;



typedef struct
{
    const char *name;
    const char *description;
    const uint16_t index;
    const uint16_t count;
    ODIN_parameter_t *parameters[];
} ODIN_parameter_group_t;

typedef struct
{
    const uint16_t count;
    ODIN_parameter_group_t *groups[];
} ODIN_store_t;

#define ODIN_SUCCESS 0
#define ODIN_ERROR -20
#define ODIN_ERROR_NO_PARAMETER -1
#define ODIN_ERROR_PARAMETER_NOT_FOUND -6
#define ODIN_ERROR_SIZE_MISMATCH -2
#define ODIN_ERROR_PERMISSION_DENIED -3
#define ODIN_ERROR_UNSUPPORTED_FORMAT -4

#define ODIN_READ_ACCESS 0
#define ODIN_WRITE_ACCESS 1

// Basic access
int ODIN_parameter_read(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
int ODIN_parameter_write(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
bool ODIN_check_access(ODIN_parameter_t *parameter, uint16_t access_group, uint16_t operation);
const char *ODIN_error_to_string(int error);

// Basic parameter retrieval
ODIN_parameter_group_t *ODIN_find_group_by_name(ODIN_store_t *OD, const char *name);
ODIN_parameter_group_t *ODIN_find_group_by_id(ODIN_store_t *OD, uint16_t index);
ODIN_parameter_t *ODIN_find_parameter_by_name(ODIN_store_t *OD, const char *group_name, const char *parameter_name);
ODIN_parameter_t *ODIN_find_parameter_by_id(ODIN_store_t *OD, uint32_t index);

int ODIN_parameter_read_as_uint16(ODIN_parameter_t *parameter, uint16_t *data, uint16_t access_group);
int ODIN_parameter_write_as_uint16(ODIN_parameter_t *parameter, uint16_t data, uint16_t access_group);
int ODIN_parameter_read_as_int16(ODIN_parameter_t *parameter, int16_t *data, uint16_t access_group);
int ODIN_parameter_write_as_int16(ODIN_parameter_t *parameter, int16_t data, uint16_t access_group);
int ODIN_parameter_read_as_float(ODIN_parameter_t *parameter, float *data, uint16_t access_group);
int ODIN_parameter_write_as_float(ODIN_parameter_t *parameter, float data, uint16_t access_group);
int ODIN_parameter_read_as_bool(ODIN_parameter_t *parameter, bool *data, uint16_t access_group);
int ODIN_parameter_write_as_bool(ODIN_parameter_t *parameter, bool data, uint16_t access_group);
int ODIN_parameter_read_as_uint8(ODIN_parameter_t *parameter, uint8_t *data, uint16_t access_group);
int ODIN_parameter_write_as_uint8(ODIN_parameter_t *parameter, uint8_t data, uint16_t access_group);
int ODIN_parameter_read_as_int8(ODIN_parameter_t *parameter, int8_t *data, uint16_t access_group);
int ODIN_parameter_write_as_int8(ODIN_parameter_t *parameter, int8_t data, uint16_t access_group);

int ODIN_parameter_get_number(ODIN_parameter_t *parameter, const uint8_t *param_data, size_t param_size, float *data);
int ODIN_parameter_set_number(ODIN_parameter_t *parameter, uint8_t *param_data, size_t param_size, float data);

#endif
