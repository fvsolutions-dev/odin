#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "codec/string_codec.h"
#include "odin.h"
#include "odin_core.h"
#include "odin_security.h"
#include "unity.h"

void setUp(void) {}
void tearDown(void) {}

/* Internal access skips the flag check, so tests can leave flags=0. */
#define INTERNAL ODIN_ACCESS_GROUP_INTERNAL

void test_scalar_to_string(void)
{
    uint32_t storage = 12345;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .element_size = sizeof(uint32_t),
        .max_elements = 1,
        .data = &storage,
        .name_and_description = "scalar",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    TEST_ASSERT_EQUAL_STRING("12345", out);
}

void test_short_array_to_string(void)
{
    uint16_t storage[4] = {1, 2, 3, 4};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 4,
        .data = storage,
        .name_and_description = "arr",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    TEST_ASSERT_EQUAL_STRING("[1, 2, 3, 4]", out);
}

/* Bug 3: an array whose payload exceeds the old 128 B scratch buffer must
   still render (truncated with "..."), not return "Buffer too small". */
void test_long_array_does_not_overflow(void)
{
    uint16_t storage[128];
    for (int i = 0; i < 128; i++) storage[i] = (uint16_t)i;
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 128,  /* 256 B payload, > old 128 B read buffer */
        .data = storage,
        .name_and_description = "long",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);                       /* no error code */
    TEST_ASSERT_LESS_OR_EQUAL(sizeof(out), (size_t)n + 1);
    TEST_ASSERT_EQUAL('[', out[0]);
    TEST_ASSERT_NOT_NULL(strstr(out, "..."));             /* truncated, not failed */
}

/* A vector laid out exactly like the generated ODIN_vector_structure_t:
   a size_t count followed by the element storage. */
typedef struct {
    size_t num_elements;
    uint16_t data[8];
} u16_vector_t;

void test_vector_to_string(void)
{
    u16_vector_t v = {.num_elements = 3, .data = {10, 20, 30}};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 8,
        .data = &v,
        .name_and_description = "vec",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    TEST_ASSERT_EQUAL_STRING("[10, 20, 30]", out);
}

/* Bug 2: a vector of a custom struct with no string-codec extension must
   render a graceful summary, not "Not supported". */
typedef struct {
    uint8_t a;
    uint8_t b;
    uint16_t c;
} demo_step_t;

typedef struct {
    size_t num_elements;
    demo_step_t data[8];
} demo_step_vector_t;

void test_custom_struct_vector_summary(void)
{
    demo_step_vector_t v = {.num_elements = 3};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_step_t),
        .max_elements = 8,
        .data = &v,
        .name_and_description = "steps",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);  /* not ODIN_ERROR_NOT_SUPPORTED */
    char expect[64];
    snprintf(expect, sizeof(expect), "<3 elements x %u B (custom)>",
             (unsigned)sizeof(demo_step_t));
    TEST_ASSERT_EQUAL_STRING(expect, out);
}

/* A single custom element (scalar parameter, not array) summarises too. */
void test_custom_scalar_summary(void)
{
    demo_step_t s = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_step_t),
        .max_elements = 1,
        .data = &s,
        .name_and_description = "one_step",
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    char expect[64];
    snprintf(expect, sizeof(expect), "<%u B struct>", (unsigned)sizeof(demo_step_t));
    TEST_ASSERT_EQUAL_STRING(expect, out);
}

/* Custom string-codec extension: a struct WITH a string_serialiser attached
   must route through the extension's to_string() — both as a scalar parameter
   and per-element in a vector — instead of the generic "<... (custom)>"
   summary. Models the wifi networks serializer (SSID + masked secret). */
typedef struct {
    char  ssid[8];
    char  secret[8];
} demo_net_t;

static int demo_net_to_string(const ODIN_parameter_t *parameter, const void *data,
                              size_t size, char *buffer, size_t buffer_size)
{
    (void)parameter;
    (void)size;
    const demo_net_t *n = (const demo_net_t *)data;
    return snprintf(buffer, buffer_size, "ssid=\"%s\" pass=%s",
                    n->ssid, n->secret[0] ? "****" : "(none)");
}

static ODIN_string_serialisation_extension_ops_t demo_net_ops = {
    .to_string   = demo_net_to_string,
    .from_string = NULL,
};

static ODIN_extension_t demo_net_ext = {
    .type = ODIN_EXTENSION_TYPE_STRING_CODEC,
    .ops  = &demo_net_ops,
    .data = NULL,
    .next = NULL,
};

void test_custom_scalar_extension_to_string(void)
{
    demo_net_t s = {.ssid = "home", .secret = "hunter2"};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_net_t),
        .max_elements = 1,
        .data = &s,
        .name_and_description = "net",
        .extension = &demo_net_ext,
    };

    char out[64];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    TEST_ASSERT_EQUAL_STRING("ssid=\"home\" pass=****", out);  /* secret masked */
}

typedef struct {
    size_t     num_elements;
    demo_net_t data[4];
} demo_net_vector_t;

void test_custom_vector_extension_to_string(void)
{
    demo_net_vector_t v = {.num_elements = 2};
    strcpy(v.data[0].ssid, "a");   strcpy(v.data[0].secret, "x");
    strcpy(v.data[1].ssid, "b");   v.data[1].secret[0] = '\0';
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_net_t),
        .max_elements = 4,
        .data = &v,
        .name_and_description = "nets",
        .extension = &demo_net_ext,
    };

    char out[128];
    int n = ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);  /* per-element extension, not the summary */
    TEST_ASSERT_EQUAL_STRING("[ssid=\"a\" pass=****, ssid=\"b\" pass=(none)]", out);
}

/* Regression: a vector whose per-element rendering is LONG (~50 B, like the
   test_manager step serialiser) must truncate with "..." inside the buffer.
   The old code added snprintf's would-have-written length to `len` on
   truncation, then wrote the ", " separator and "..." out of bounds —
   corrupting the caller's stack (seen on target as a task-watchdog wedge in
   eros_console during odin-dump). Canary bytes around the output buffer
   catch any out-of-bounds write. */
typedef struct {
    uint8_t  red, uv;
    uint16_t als_ms, uvs_ms;
} demo_step_long_t;

static int demo_step_long_to_string(const ODIN_parameter_t *parameter, const void *data,
                                    size_t size, char *buffer, size_t buffer_size)
{
    (void)parameter;
    (void)size;
    const demo_step_long_t *s = (const demo_step_long_t *)data;
    return snprintf(buffer, buffer_size,
                    "{red=%umA uv=%umA als=%ums uvs=%ums gain als=3 uv=18}",
                    s->red, s->uv, s->als_ms, s->uvs_ms);
}

static ODIN_string_serialisation_extension_ops_t demo_step_long_ops = {
    .to_string   = demo_step_long_to_string,
    .from_string = NULL,
};

static ODIN_extension_t demo_step_long_ext = {
    .type = ODIN_EXTENSION_TYPE_STRING_CODEC,
    .ops  = &demo_step_long_ops,
    .data = NULL,
    .next = NULL,
};

typedef struct {
    size_t           num_elements;
    demo_step_long_t data[24];
} demo_step_long_vector_t;

void test_long_custom_elements_truncate_in_bounds(void)
{
    demo_step_long_vector_t v = {.num_elements = 24};
    for (int i = 0; i < 24; i++) {
        v.data[i] = (demo_step_long_t){.red = (uint8_t)i, .uv = 32, .als_ms = 50, .uvs_ms = 400};
    }
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_step_long_t),
        .max_elements = 24,
        .data = &v,
        .name_and_description = "steps",
        .extension = &demo_step_long_ext,
    };

    /* 512 B mirrors ODIN_dump_parameter's stack buffer; canaries on both
       sides detect the out-of-bounds separator/ellipsis writes. */
    struct {
        char head[16];
        char out[512];
        char tail[64];
    } guarded;
    memset(guarded.head, 0xAA, sizeof(guarded.head));
    memset(guarded.tail, 0xAA, sizeof(guarded.tail));

    int n = ODIN_encode_parameter_to_string(&p, guarded.out, sizeof(guarded.out), INTERNAL);
    TEST_ASSERT_GREATER_THAN(0, n);
    TEST_ASSERT_LESS_THAN((int)sizeof(guarded.out), n + 1);   /* len within buffer */
    TEST_ASSERT_EQUAL('[', guarded.out[0]);
    TEST_ASSERT_NOT_NULL(strstr(guarded.out, "..."));         /* truncated, not failed */
    TEST_ASSERT_EQUAL(']', guarded.out[n - 1]);               /* properly closed */
    for (size_t i = 0; i < sizeof(guarded.head); i++) {
        TEST_ASSERT_EQUAL_HEX8(0xAA, (uint8_t)guarded.head[i]);
    }
    for (size_t i = 0; i < sizeof(guarded.tail); i++) {
        TEST_ASSERT_EQUAL_HEX8(0xAA, (uint8_t)guarded.tail[i]);
    }
}

/* Decoding arrays and vectors: texts for char elements, "[a, b]" lists for the others */

typedef struct {
    size_t num_elements;
    char data[8];
} char_vector_t;

static ODIN_parameter_t text_vector(char_vector_t *v)
{
    return (ODIN_parameter_t){
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CHAR,
        .element_size = 1,
        .max_elements = 8,
        .data = v,
        .name_and_description = "text",
    };
}

void test_text_vector_from_string(void)
{
    char_vector_t v = {0};
    ODIN_parameter_t p = text_vector(&v);

    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "hello", INTERNAL));
    TEST_ASSERT_EQUAL(5, v.num_elements);
    TEST_ASSERT_EQUAL_MEMORY("hello", v.data, 5);

    /* The quotes, as the encoder prints a text, are optional */
    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "\"ab\"", INTERNAL));
    TEST_ASSERT_EQUAL(2, v.num_elements);
    TEST_ASSERT_EQUAL_MEMORY("ab", v.data, 2);

    /* Empty */
    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "\"\"", INTERNAL));
    TEST_ASSERT_EQUAL(0, v.num_elements);
}

void test_text_vector_too_long_is_refused(void)
{
    char_vector_t v = {.num_elements = 2, .data = "ab"};
    ODIN_parameter_t p = text_vector(&v);

    TEST_ASSERT_EQUAL(ODIN_ERROR_SIZE_MISMATCH,
                      ODIN_decode_string_to_parameter(&p, "123456789", INTERNAL));
    TEST_ASSERT_EQUAL(2, v.num_elements); /* unchanged */
}

void test_text_round_trip(void)
{
    char_vector_t v = {0};
    ODIN_parameter_t p = text_vector(&v);
    char out[32];

    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "net 5G", INTERNAL));
    TEST_ASSERT_GREATER_THAN(0, ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL));
    TEST_ASSERT_EQUAL_STRING("\"net 5G\"", out);
    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, out, INTERNAL));
    TEST_ASSERT_EQUAL(6, v.num_elements);
    TEST_ASSERT_EQUAL_MEMORY("net 5G", v.data, 6);
}

void test_text_array_is_padded_with_zeros(void)
{
    char storage[6] = "xxxxx";
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_CHAR,
        .element_size = 1,
        .max_elements = 6,
        .data = storage,
        .name_and_description = "text_array",
    };

    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "ab", INTERNAL));
    TEST_ASSERT_EQUAL_MEMORY("ab\0\0\0\0", storage, 6);
}

void test_number_vector_from_string(void)
{
    u16_vector_t v = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 8,
        .data = &v,
        .name_and_description = "vec",
    };
    char out[64];

    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "[1, 2, 300]", INTERNAL));
    TEST_ASSERT_EQUAL(3, v.num_elements);
    TEST_ASSERT_EQUAL(300, v.data[2]);

    /* Without brackets, and back to the encoder's form */
    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, " 7,8 ", INTERNAL));
    TEST_ASSERT_EQUAL(2, v.num_elements);
    TEST_ASSERT_GREATER_THAN(0, ODIN_encode_parameter_to_string(&p, out, sizeof(out), INTERNAL));
    TEST_ASSERT_EQUAL_STRING("[7, 8]", out);

    /* Empty */
    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "[]", INTERNAL));
    TEST_ASSERT_EQUAL(0, v.num_elements);
}

void test_number_vector_errors(void)
{
    u16_vector_t v = {.num_elements = 1, .data = {5}};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .element_size = sizeof(uint16_t),
        .max_elements = 8,
        .data = &v,
        .name_and_description = "vec",
    };

    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_decode_string_to_parameter(&p, "[1, x]", INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_decode_string_to_parameter(&p, "[1, 2", INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_INVALID_ARGUMENT,
                      ODIN_decode_string_to_parameter(&p, "1,,2", INTERNAL));
    TEST_ASSERT_EQUAL(ODIN_ERROR_SIZE_MISMATCH,
                      ODIN_decode_string_to_parameter(&p, "1,2,3,4,5,6,7,8,9", INTERNAL));
    TEST_ASSERT_EQUAL(1, v.num_elements); /* unchanged */
    TEST_ASSERT_EQUAL(5, v.data[0]);
}

void test_number_array_needs_all_elements(void)
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

    TEST_ASSERT_GREATER_OR_EQUAL(0, ODIN_decode_string_to_parameter(&p, "[1, 2, 3, 4]", INTERNAL));
    TEST_ASSERT_EQUAL(4, storage[3]);
    TEST_ASSERT_EQUAL(ODIN_ERROR_SIZE_MISMATCH,
                      ODIN_decode_string_to_parameter(&p, "[9, 9]", INTERNAL));
    TEST_ASSERT_EQUAL(1, storage[0]); /* unchanged */
}

void test_custom_vector_from_string_is_not_supported(void)
{
    demo_step_vector_t v = {0};
    ODIN_parameter_t p = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CUSTOM,
        .element_size = sizeof(demo_step_t),
        .max_elements = 8,
        .data = &v,
        .name_and_description = "steps",
    };

    TEST_ASSERT_EQUAL(ODIN_ERROR_NOT_SUPPORTED,
                      ODIN_decode_string_to_parameter(&p, "[1]", INTERNAL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_scalar_to_string);
    RUN_TEST(test_short_array_to_string);
    RUN_TEST(test_long_array_does_not_overflow);
    RUN_TEST(test_vector_to_string);
    RUN_TEST(test_custom_struct_vector_summary);
    RUN_TEST(test_custom_scalar_summary);
    RUN_TEST(test_custom_scalar_extension_to_string);
    RUN_TEST(test_custom_vector_extension_to_string);
    RUN_TEST(test_long_custom_elements_truncate_in_bounds);
    RUN_TEST(test_text_vector_from_string);
    RUN_TEST(test_text_vector_too_long_is_refused);
    RUN_TEST(test_text_round_trip);
    RUN_TEST(test_text_array_is_padded_with_zeros);
    RUN_TEST(test_number_vector_from_string);
    RUN_TEST(test_number_vector_errors);
    RUN_TEST(test_number_array_needs_all_elements);
    RUN_TEST(test_custom_vector_from_string_is_not_supported);
    return UNITY_END();
}
