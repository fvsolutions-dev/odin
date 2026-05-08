#include <stdint.h>
#include <string.h>

#include "odin.h"
#include "odin_core.h"
#include "odin_security.h"
#include "unity.h"

void setUp(void) {}
void tearDown(void) {}

/* Internal access skips the flag check, so tests can leave flags=0. */
#define INTERNAL ODIN_ACCESS_GROUP_INTERNAL

void test_get_data_size_for_scalar(void)
{
    uint32_t storage = 0;
    ODIN_parameter_t p = {
        .global_index = 0,
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    TEST_ASSERT_EQUAL(sizeof(uint32_t), ODIN_get_data_size(&p));
    TEST_ASSERT_EQUAL(sizeof(uint32_t), ODIN_get_max_data_size(&p));
}

void test_get_data_size_for_array(void)
{
    uint16_t storage[8] = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 8,
        .data = storage,
        .name_and_description = "arr",
    };

    TEST_ASSERT_EQUAL(8 * sizeof(uint16_t), ODIN_get_data_size(&p));
    TEST_ASSERT_EQUAL(8 * sizeof(uint16_t), ODIN_get_max_data_size(&p));
}

void test_scalar_round_trip(void)
{
    uint32_t storage = 0;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    uint32_t in = 0xDEADBEEF;
    int written = ODIN_parameter_write(&p, &in, sizeof(in), INTERNAL);
    TEST_ASSERT_EQUAL((int)sizeof(in), written);
    TEST_ASSERT_EQUAL_HEX32(0xDEADBEEF, storage);

    uint32_t out = 0;
    int read = ODIN_parameter_read(&p, &out, sizeof(out), INTERNAL);
    TEST_ASSERT_EQUAL((int)sizeof(out), read);
    TEST_ASSERT_EQUAL_HEX32(0xDEADBEEF, out);
}

void test_write_size_mismatch_rejected(void)
{
    uint32_t storage = 0;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    uint16_t too_small = 5;
    TEST_ASSERT_EQUAL(ODIN_ERROR_SIZE_MISMATCH,
                      ODIN_parameter_write(&p, &too_small, sizeof(too_small), INTERNAL));
}

void test_null_arguments_rejected(void)
{
    uint32_t storage = 0;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };
    uint32_t v = 0;

    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_parameter_read(NULL, &v, sizeof(v), INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_parameter_read(&p, NULL, sizeof(v), INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_parameter_write(NULL, &v, sizeof(v), INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_parameter_write(&p, NULL, sizeof(v), INTERNAL));
}

void test_array_element_round_trip(void)
{
    uint16_t storage[4] = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 4,
        .data = storage,
        .name_and_description = "arr",
    };

    uint16_t in = 0xABCD;
    TEST_ASSERT_EQUAL((int)sizeof(in),
                      ODIN_array_write_element(&p, 2, &in, sizeof(in), INTERNAL));
    TEST_ASSERT_EQUAL_HEX16(0xABCD, storage[2]);

    uint16_t out = 0;
    TEST_ASSERT_EQUAL((int)sizeof(out),
                      ODIN_array_read_element(&p, 2, &out, sizeof(out), INTERNAL));
    TEST_ASSERT_EQUAL_HEX16(0xABCD, out);
}

void test_array_index_out_of_bounds(void)
{
    uint16_t storage[4] = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 4,
        .data = storage,
        .name_and_description = "arr",
    };

    uint16_t in = 1;
    TEST_ASSERT_EQUAL(ODIN_ERROR_SIZE_MISMATCH,
                      ODIN_array_write_element(&p, 4, &in, sizeof(in), INTERNAL));
}

void test_array_op_rejects_non_array(void)
{
    uint32_t storage = 0;
    ODIN_parameter_t scalar = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    uint32_t v = 0;
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_array_write_element(&scalar, 0, &v, sizeof(v), INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_array_read_element(&scalar, 0, &v, sizeof(v), INTERNAL));
}

void test_read_into_buffer_too_small(void)
{
    uint32_t storage = 0xCAFEF00D;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    uint16_t small_buf = 0;
    TEST_ASSERT_EQUAL(ODIN_ERROR_BUFFER_TOO_SMALL,
                      ODIN_parameter_read_into_buffer(&p, &small_buf, sizeof(small_buf), INTERNAL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_get_data_size_for_scalar);
    RUN_TEST(test_get_data_size_for_array);
    RUN_TEST(test_scalar_round_trip);
    RUN_TEST(test_write_size_mismatch_rejected);
    RUN_TEST(test_null_arguments_rejected);
    RUN_TEST(test_array_element_round_trip);
    RUN_TEST(test_array_index_out_of_bounds);
    RUN_TEST(test_array_op_rejects_non_array);
    RUN_TEST(test_read_into_buffer_too_small);
    return UNITY_END();
}
