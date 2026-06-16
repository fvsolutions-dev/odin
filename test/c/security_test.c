#include "odin.h"
#include "odin_security.h"
#include "unity.h"

void setUp(void) {}
void tearDown(void) {}

/* Build a parameter whose flags grant the given access bits. */
static ODIN_parameter_t make_parameter_with_flags(uint16_t flags)
{
    ODIN_parameter_t p = {0};
    p.flags = flags;
    p.element_type = ODIN_ELEMENT_TYPE_UINT8;
    p.element_size = sizeof(uint8_t);
    p.max_elements = 1;
    p.odin_type = ODIN_TYPE_PARAMETER;
    p.name_and_description = "p";
    return p;
}

void test_internal_group_always_allowed(void)
{
    ODIN_parameter_t p = make_parameter_with_flags(0);
    TEST_ASSERT_TRUE(ODIN_check_access(&p, ODIN_ACCESS_GROUP_INTERNAL, ODIN_ACCESS_READ));
    TEST_ASSERT_TRUE(ODIN_check_access(&p, ODIN_ACCESS_GROUP_INTERNAL, ODIN_ACCESS_WRITE));
}

void test_null_parameter_denied(void)
{
    TEST_ASSERT_FALSE(ODIN_check_access(NULL, ODIN_ACCESS_GROUP_0, ODIN_ACCESS_READ));
}

void test_group0_read_allowed_when_flag_set(void)
{
    /* Grant only group 0 read. */
    ODIN_parameter_t p = make_parameter_with_flags(ODIN_ACCESS_READ & ODIN_ACCESS_GROUP_0);
    TEST_ASSERT_TRUE(ODIN_check_access(&p, ODIN_ACCESS_GROUP_0, ODIN_ACCESS_READ));
}

void test_group0_write_denied_when_only_read_set(void)
{
    ODIN_parameter_t p = make_parameter_with_flags(ODIN_ACCESS_READ & ODIN_ACCESS_GROUP_0);
    TEST_ASSERT_FALSE(ODIN_check_access(&p, ODIN_ACCESS_GROUP_0, ODIN_ACCESS_WRITE));
}

void test_other_group_denied_when_only_group0_allowed(void)
{
    ODIN_parameter_t p = make_parameter_with_flags(ODIN_ACCESS_READ & ODIN_ACCESS_GROUP_0);
    TEST_ASSERT_FALSE(ODIN_check_access(&p, ODIN_ACCESS_GROUP_1, ODIN_ACCESS_READ));
}

void test_validate_returns_permission_denied(void)
{
    ODIN_parameter_t p = make_parameter_with_flags(0);
    TEST_ASSERT_EQUAL(ODIN_ERROR_PERMISSION_DENIED,
                      ODIN_validate_access(&p, ODIN_ACCESS_GROUP_0, ODIN_ACCESS_READ));
}

void test_validate_succeeds_for_internal(void)
{
    ODIN_parameter_t p = make_parameter_with_flags(0);
    TEST_ASSERT_EQUAL(ODIN_SUCCESS,
                      ODIN_validate_access(&p, ODIN_ACCESS_GROUP_INTERNAL, ODIN_ACCESS_WRITE));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_internal_group_always_allowed);
    RUN_TEST(test_null_parameter_denied);
    RUN_TEST(test_group0_read_allowed_when_flag_set);
    RUN_TEST(test_group0_write_denied_when_only_read_set);
    RUN_TEST(test_other_group_denied_when_only_group0_allowed);
    RUN_TEST(test_validate_returns_permission_denied);
    RUN_TEST(test_validate_succeeds_for_internal);
    return UNITY_END();
}
