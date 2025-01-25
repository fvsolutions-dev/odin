#include <gtest/gtest.h>
#include <stdint.h>

#include <cstdint>

extern "C" {
#include "OD.h"
#include "odin_codec.h"

#include "odin.h"
#include "odin_core.h"
}

bool validate_recursively(const ODIN_parameter_group_t *group, odin_access_group_t access_group, odin_acces_operation_t operation,
                          odin_error_t expected_result) {
    int error = ODIN_SUCCESS;

    for (int i = 0; i < group->count; i++) {
        ODIN_parameter_generic_t *parameter = (ODIN_parameter_generic_t *)group->parameters[i];

        switch (parameter->odin_type) {
            case ODIN_TYPE_PARAMETER:
            case ODIN_TYPE_ARRAY:
            case ODIN_TYPE_VECTOR: {
                ODIN_parameter_t *parameter = (ODIN_parameter_t *)group->parameters[i];
                error = ODIN_validate_access(parameter, access_group, operation);

                if (error != expected_result) {
                    // print to sterror
                    printf("Wrong access for %s\n", parameter->name_and_description);
                    return false;
                }

            } break;

            case ODIN_TYPE_GROUP: {
                ODIN_parameter_group_t *parameter = (ODIN_parameter_group_t *)group->parameters[i];
                bool ok = validate_recursively(parameter, access_group, operation, expected_result);

                if (!ok) {
                    return false;
                }
                break;
            }
        }
    }
    return true;
}

// Single parameter tests
TEST(ODINParameterBasicAccess, TestCases) {
    int32_t output_data = 0;
    // clang-format off

    // Disk should have RW permissions on another group but not on basic group
    EXPECT_EQ(validate_recursively(&odin_store_another_group, ODIN_ACCESS_DISK, ODIN_ACCESS_READ,ODIN_SUCCESS), true);
    EXPECT_EQ(validate_recursively(&odin_store_another_group, ODIN_ACCESS_DISK, ODIN_ACCESS_WRITE,ODIN_SUCCESS), true);
    EXPECT_EQ(validate_recursively(&odin_store_basic_group, ODIN_ACCESS_DISK, ODIN_ACCESS_READ,ODIN_ERROR_PERMISSION_DENIED), true);
    EXPECT_EQ(validate_recursively(&odin_store_basic_group, ODIN_ACCESS_DISK, ODIN_ACCESS_WRITE,ODIN_ERROR_PERMISSION_DENIED), true);
    
    //Guest should have no permissions on any group
    EXPECT_EQ(validate_recursively(&odin_store, ODIN_ACCESS_GUEST, ODIN_ACCESS_READ,ODIN_ERROR_PERMISSION_DENIED), true);
    EXPECT_EQ(validate_recursively(&odin_store, ODIN_ACCESS_GUEST, ODIN_ACCESS_WRITE,ODIN_ERROR_PERMISSION_DENIED), true);
    EXPECT_EQ(validate_recursively(&odin_store, ODIN_ACCESS_GUEST, ODIN_ACCESS_LOG_WRITE,ODIN_ERROR_PERMISSION_DENIED), true);

    // BLE should habe no permissions on another group but should have read permissions on basic group but no write permissions on test_variable_B
    EXPECT_EQ(validate_recursively(&odin_store_another_group, ODIN_ACCESS_BLE, ODIN_ACCESS_READ,ODIN_ERROR_PERMISSION_DENIED), true);
    EXPECT_EQ(validate_recursively(&odin_store_another_group, ODIN_ACCESS_BLE, ODIN_ACCESS_WRITE,ODIN_ERROR_PERMISSION_DENIED), true);
    EXPECT_EQ(validate_recursively(&odin_store_basic_group, ODIN_ACCESS_BLE, ODIN_ACCESS_READ,ODIN_SUCCESS), true);
    EXPECT_EQ(validate_recursively(&odin_store_basic_group, ODIN_ACCESS_BLE, ODIN_ACCESS_WRITE,ODIN_SUCCESS), false);
    EXPECT_EQ(ODIN_validate_access(&root.basic_group.test_variable_B, ODIN_ACCESS_BLE, ODIN_ACCESS_WRITE), ODIN_ERROR_PERMISSION_DENIED);
    EXPECT_EQ(ODIN_validate_access(&root.basic_group.test_variable_B, ODIN_ACCESS_BLE, ODIN_ACCESS_READ), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_validate_access(&root.basic_group.test_variable_A, ODIN_ACCESS_BLE, ODIN_ACCESS_WRITE), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_validate_access(&root.basic_group.test_variable_A, ODIN_ACCESS_BLE, ODIN_ACCESS_READ), ODIN_SUCCESS);

    // CLI whould be able to log_write on all groups
    EXPECT_EQ(validate_recursively(&odin_store, ODIN_ACCESS_CLI, ODIN_ACCESS_LOG_WRITE,ODIN_SUCCESS), true);
    EXPECT_EQ(validate_recursively(&odin_store, ODIN_ACCESS_CLI, ODIN_ACCESS_READ,ODIN_SUCCESS), true);

    // clang-format on
}

// Group 0 RW
// Group 1 R
// Group 2 No access

uint32_t value = 0;
ODIN_parameter_t test_param = {
    .odin_type = ODIN_TYPE_PARAMETER,
    .element_type = ODIN_ELEMENT_TYPE_INT32,
    .flags = (ODIN_ACCESS_GROUP_0 & (ODIN_ACCESS_READ | ODIN_ACCESS_WRITE)) | (ODIN_ACCESS_GROUP_1 & (ODIN_ACCESS_READ)),
    .element_size = sizeof(int32_t),
    .data = &value,
    .name_and_description = "test_variable_i32"};

// Single parameter tests
TEST(ODINParameterBasicAccess, ReadWrite) {
    int32_t output_data = 0;

    // clang-format off
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_0), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_1), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_parameter_read(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_2), ODIN_ERROR_PERMISSION_DENIED);

    EXPECT_GE(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);
    EXPECT_GE(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_0), ODIN_SUCCESS);
    EXPECT_EQ(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_1), ODIN_ERROR_PERMISSION_DENIED);
    EXPECT_EQ(ODIN_parameter_write(&test_param, &output_data, sizeof(output_data), ODIN_ACCESS_GROUP_2), ODIN_ERROR_PERMISSION_DENIED);
    // clang-format on
}