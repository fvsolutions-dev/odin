
#include <OD.h>
#include <stdio.h>
#include <string.h>

#include "odin_codec.h"
#include "odin_core.h"
#include "odin_lookup.h"
#include "odin_utils.h"

int print_vector_write() {
    int data[10] = {0};

    for (int i = 0; i < 10; i++) {
        data[i] = i * 101;

        int ret = ODIN_parameter_write(&root.i32_variable_length_array, data, i * 4, 0);

        if (ret < 0) {
            printf("Error: %s\n", ODIN_error_to_string(ret));
            return -1;
        }

        char buffer[256] = {0};
        int len = ODIN_encode_parameter_to_string(&root.i32_variable_length_array, buffer, sizeof(buffer), 0);
        printf("%s\n", buffer);
    }
    return 0;
}

void id_lookup(uint32_t index) {
    const ODIN_parameter_t *parameter = ODIN_get_parameter_by_id(&odin_store, index, 0);
    if (parameter == NULL) {
        printf("Parameter not found\n");
        return;
    }
    printf("parameter: %s\n", parameter->name_and_description);
}

void proto_export() {
    parameter_encode_operation_t operation;
    ODIN_encode_parameter_to_protobuff_init(&root.test_variable_u8, &operation, ODIN_ACCESS_GROUP_INTERNAL);

    uint8_t buffer[256] = {0};
    int ret = ODIN_encode_parameter_to_protobuff_buffer(&operation, buffer, sizeof(buffer));
    if (ret < 0) {
        printf("Error: %s\n", ODIN_error_to_string(ret));
        return;
    }

    printf("Exported %d bytes\n", ret);
    for (int i = 0; i < ret; i++) {
        printf("%02X ", buffer[i]);
    }
    printf("\n");
}

void proto_export_group() {
    parameter_group_encode_operation_t operation;
    ODIN_encode_parameter_group_to_protobuff_init(&odin_store, &operation, ODIN_ACCESS_GROUP_INTERNAL);

    uint8_t buffer[5048] = {0};
    int ret = ODIN_encode_parameter_group_to_protobuff_buffer(&operation, buffer, sizeof(buffer));
    if (ret < 0) {
        printf("Error: %s\n", ODIN_error_to_string(ret));
        return;
    }

    printf("Exported %d bytes\n", ret);
    for (int i = 0; i < ret; i++) {
        printf("%02X ", buffer[i]);
    }
    printf("\n");
}

void proto_export_file() {
    uint8_t buffer[5048] = {0};
    int ret = ODIN_encode_parameter_group_to_protobuff_file(&odin_store, "test.pb", ODIN_ACCESS_GROUP_INTERNAL);

    if (ret < 0) {
        printf("Error: %s\n", ODIN_error_to_string(ret));
        return;
    }
}

void tvl_export_group() {
    // Copy the value to the RAM

    uint8_t buffer[4096] = {0};
    int len = ODIN_encode_parameter_group_to_bytes(&odin_store, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL);

    if (len < 0) {
        printf("Error: %s\n", ODIN_error_to_string(len));
        return;
    }

    printf("Exported %d bytes\n", len);
    for (int i = 0; i < len; i++) {
        printf("%02X ", buffer[i]);
    }
}

int main() {
    proto_export_file();
    proto_export();
    proto_export_group();
    tvl_export_group();

    return 0;
    // id_lookup(0x0A000000);
    id_lookup(0x10030000);
    return 0;
    print_vector_write();
    return 0;
    char buffer[256] = {0};

    int len = ODIN_encode_parameter_to_string(&root.u32_array, buffer, sizeof(buffer), 0);

    printf("len: %d\n", len);
    printf("buffer: %s\n", buffer);

    // ODIN_dump_recursive_tree(&odin_store, 0);

    printf("Finish!\n");

    return 1;
}