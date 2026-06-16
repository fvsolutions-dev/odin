/* Build a small static parameter tree by hand and exercise the lookup helpers.
 * Mirrors the layout produced by the Python C generator (see
 * src/odin_python/generators/c/model.py): each direct child of the root group
 * gets a unique value in the high 8 bits of global_index, matching shift=8. */
#include <stdint.h>

#include "odin.h"
#include "odin_lookup.h"
#include "unity.h"

void setUp(void) {}
void tearDown(void) {}

static uint32_t alpha_storage = 1;
static uint32_t beta_storage  = 2;
static uint32_t gamma_storage = 3;

static const ODIN_parameter_t alpha_param = {
    .odin_type = ODIN_TYPE_PARAMETER,
    .element_type = ODIN_ELEMENT_TYPE_UINT32,
    .global_index = 0x01000000,
    .element_size = sizeof(uint32_t),
    .max_elements = 1,
    .data = &alpha_storage,
    .name_and_description = "alpha\0first",
};

static const ODIN_parameter_t beta_param = {
    .odin_type = ODIN_TYPE_PARAMETER,
    .element_type = ODIN_ELEMENT_TYPE_UINT32,
    .global_index = 0x02000000,
    .element_size = sizeof(uint32_t),
    .max_elements = 1,
    .data = &beta_storage,
    .name_and_description = "beta\0second",
};

static const ODIN_parameter_t gamma_param = {
    .odin_type = ODIN_TYPE_PARAMETER,
    .element_type = ODIN_ELEMENT_TYPE_UINT32,
    .global_index = 0x03000000,
    .element_size = sizeof(uint32_t),
    .max_elements = 1,
    .data = &gamma_storage,
    .name_and_description = "gamma\0third",
};

static const ODIN_parameter_group_t root_group = {
    .name_and_description = "root\0",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 3,
    .parameters = {&alpha_param, &beta_param, &gamma_param},
};

void test_get_parameter_by_id_finds_each_child(void)
{
    TEST_ASSERT_EQUAL_PTR(&alpha_param,
                          ODIN_get_parameter_by_id(&root_group, 0x01000000, 0));
    TEST_ASSERT_EQUAL_PTR(&beta_param,
                          ODIN_get_parameter_by_id(&root_group, 0x02000000, 0));
    TEST_ASSERT_EQUAL_PTR(&gamma_param,
                          ODIN_get_parameter_by_id(&root_group, 0x03000000, 0));
}

void test_get_parameter_by_id_unknown_returns_null(void)
{
    TEST_ASSERT_NULL(ODIN_get_parameter_by_id(&root_group, 0x99000000, 0));
}

void test_get_parameter_by_name_finds_each_child(void)
{
    TEST_ASSERT_EQUAL_PTR(&alpha_param,
                          ODIN_get_parameter_by_name(&root_group, "alpha", '.'));
    TEST_ASSERT_EQUAL_PTR(&beta_param,
                          ODIN_get_parameter_by_name(&root_group, "beta", '.'));
}

void test_get_parameter_by_name_unknown_returns_null(void)
{
    TEST_ASSERT_NULL(ODIN_get_parameter_by_name(&root_group, "delta", '.'));
}

void test_get_parameter_group_by_id_rejects_leaf(void)
{
    /* alpha is a parameter, not a group — group lookup must reject it. */
    TEST_ASSERT_NULL(ODIN_get_parameter_group_by_id(&root_group, 0x01000000, 0));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_get_parameter_by_id_finds_each_child);
    RUN_TEST(test_get_parameter_by_id_unknown_returns_null);
    RUN_TEST(test_get_parameter_by_name_finds_each_child);
    RUN_TEST(test_get_parameter_by_name_unknown_returns_null);
    RUN_TEST(test_get_parameter_group_by_id_rejects_leaf);
    return UNITY_END();
}
