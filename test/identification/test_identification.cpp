#include <gtest/gtest.h>
#include <stdint.h>

extern "C" {
#include "OD.h"
#include "encoding/encode_string.h"
#include "odin.h"
#include "odin_core.h"
#include "odin_lookup.h"
}

// Single parameter tests
TEST(ODINParameterLookup, Nominal) {
    // Parameter lookup
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x0445FF00, 0), &root.group_2.group_3.test_variable_small);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x04200000, 0), &root.group_2.test_variable_B);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x03010000, 0), &root.group_1.test_variable_A);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x03020000, 0), &root.group_1.test_variable_B);

    // Parameter lookup with group
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0x04200000, 0), (ODIN_parameter_group_t *)NULL);

    // Group Lookup
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0x03000000, 0), &odin_store_group_1);
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0x04000000, 0), &odin_store_group_2);
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0x04400000, 0), &odin_store_group_2_group_3);

    // Group Lookup as parameter
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x03000000, 0), (ODIN_parameter_t *)NULL);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x04400000, 0), (ODIN_parameter_t *)NULL);

    // clang-format on
}

TEST(ODINParameterLookup, InvalidLookup) {
    // clang-format off

    // Parameter lookup with group
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0x04200000, 0), (ODIN_parameter_group_t *)NULL);
    EXPECT_EQ(ODIN_get_parameter_group_by_id(&odin_store, 0, 0), (ODIN_parameter_group_t *)NULL);
    
    // Group Lookup as parameter
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x03000000, 0), (ODIN_parameter_t *)NULL);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0x04400000, 0), (ODIN_parameter_t *)NULL);
    EXPECT_EQ(ODIN_get_parameter_by_id(&odin_store, 0, 0), (ODIN_parameter_t *)NULL);

    // clang-format on
}

TEST(ODINParameterLookup, NULLLookup) {
    // clang-format off

    EXPECT_EQ(ODIN_get_parameter_group_by_id(NULL, 0x04200000, 0), (ODIN_parameter_group_t *)NULL);
    EXPECT_EQ(ODIN_get_parameter_by_id(NULL, 0x03000000, 0), (ODIN_parameter_t *)NULL);

    // clang-format on
}