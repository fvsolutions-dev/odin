#ifndef ODIN_EXTENSIONS_H
#define ODIN_EXTENSIONS_H

typedef struct ODIN_parameter_t ODIN_parameter_t;

typedef struct
{
    int (*write)(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
    int (*read)(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
    
    // Validate the data before writing it to the parameter
    int (*validate)(ODIN_parameter_t *parameter, void *data, size_t size, uint16_t access_group);
} ODIN_extension_ops_t;

typedef struct
{
    ODIN_extension_ops_t *ops;
    void *data;
} ODIN_extension_t;

typedef struct
{
    float max;
    float min;
} range_parameter_t;

typedef struct
{
    ODIN_parameter_t *reference;
    float offset;
    float scale;
} mapped_parameter_t;
extern ODIN_extension_ops_t range_validator_extension;
extern ODIN_extension_ops_t parameter_mapping_extension;

#endif // ODIN_EXTENSIONS_H