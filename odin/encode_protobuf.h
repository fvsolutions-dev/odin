#include <stdbool.h>
#include <stdint.h>
#include "odin_datastore.h"
#include "odin.pb.h"

typedef struct
{
    uint16_t access_group;
    ODIN_parameter_t *parameter;
    odin_proto_parameter proto;
} parameter_encode_operation_t;

typedef struct
{
    uint16_t access_group;
    ODIN_parameter_t **parameters;
    size_t size;
    size_t count;
    odin_proto_parameter_collection proto;
} parameter_collection_encode_operation_t;

typedef struct
{
    uint16_t access_group;
    ODIN_store_t *store;
} parameter_collection_decode_operation_t;

typedef struct
{
    uint16_t access_group;
    odin_proto_parameter *proto;
    ODIN_store_t *store;
} parameter_decode_operation_t;

// Single parameter encoding
void ODIN_protobuff_encode_init(ODIN_parameter_t *parameter, parameter_encode_operation_t *operation, uint16_t access_group);
int ODIN_protobuff_export_to_stream(parameter_encode_operation_t *operation, pb_ostream_t *stream);
int ODIN_protobuff_export_to_buffer(parameter_encode_operation_t *operation, uint8_t *buffer, size_t size);

// Parameter collection encoding
void ODIN_protobuff_encode_collection_init(ODIN_parameter_t **parameter_buffer, size_t size, bool is_populated, parameter_collection_encode_operation_t *operation, uint16_t access_group);

int ODIN_add_parameter_to_collection(parameter_collection_encode_operation_t *operation, ODIN_parameter_t *parameter);
int ODIN_add_group_to_collection(parameter_collection_encode_operation_t *operation, ODIN_parameter_group_t *group);
int ODIN_add_store_to_collection(parameter_collection_encode_operation_t *operation, ODIN_store_t *store);

int ODIN_protobuff_export_collection_to_buffer(parameter_collection_encode_operation_t *operation, uint8_t *buffer, size_t size);
int ODIN_protobuff_export_collection_to_stream(parameter_collection_encode_operation_t *operation, pb_ostream_t *stream);

// Parameter collection decoding
int ODIN_protobuff_import_params_from_buffer(uint8_t *buffer, size_t size, ODIN_store_t *store, uint16_t access_group);
int ODIN_protobuff_import_params_from_stream(pb_istream_t *stream, ODIN_store_t *store, uint16_t access_group);

int ODIN_protobuff_export_store_to_file(ODIN_store_t *store, const char *filename, uint16_t access_group);
int ODIN_protobuff_export_group_to_file(ODIN_parameter_group_t *group, const char *filename, uint16_t access_group);
int ODIN_protobuff_import_from_file(ODIN_store_t *store, const char *filename, uint16_t access_group);
