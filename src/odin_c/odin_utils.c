#include "odin_utils.h"

#include <stdio.h>
#include <string.h>

#include "ansi_colors.h"
#include "extensions/extensions.h"  // ODIN_type_descriptor_t, find_extension, COMPOSITE
#include "odin.h"
#include "odin_codec.h"

// Render one primitive struct field (read unaligned-safe: the reading structs
// are packed). Nested CUSTOM fields have no resolvable sub-descriptor here, so
// they fall through to a size note.
static void dump_render_field(char *buf, size_t cap, uint8_t element_type,
                              const uint8_t *p, uint16_t size) {
    switch (element_type) {
        case ODIN_ELEMENT_TYPE_BOOL:    snprintf(buf, cap, "%s", *p ? "true" : "false"); break;
        case ODIN_ELEMENT_TYPE_HEX:     snprintf(buf, cap, "0x%02X", *p); break;
        case ODIN_ELEMENT_TYPE_UINT8:   snprintf(buf, cap, "%u", (unsigned)*p); break;
        case ODIN_ELEMENT_TYPE_INT8:    snprintf(buf, cap, "%d", (int)(int8_t)*p); break;
        case ODIN_ELEMENT_TYPE_UINT16:  { uint16_t v; memcpy(&v, p, 2); snprintf(buf, cap, "%u", v); } break;
        case ODIN_ELEMENT_TYPE_INT16:   { int16_t  v; memcpy(&v, p, 2); snprintf(buf, cap, "%d", v); } break;
        case ODIN_ELEMENT_TYPE_UINT32:  { uint32_t v; memcpy(&v, p, 4); snprintf(buf, cap, "%lu", (unsigned long)v); } break;
        case ODIN_ELEMENT_TYPE_INT32:   { int32_t  v; memcpy(&v, p, 4); snprintf(buf, cap, "%ld", (long)v); } break;
        case ODIN_ELEMENT_TYPE_UINT64:  { uint64_t v; memcpy(&v, p, 8); snprintf(buf, cap, "%llu", (unsigned long long)v); } break;
        case ODIN_ELEMENT_TYPE_INT64:   { int64_t  v; memcpy(&v, p, 8); snprintf(buf, cap, "%lld", (long long)v); } break;
        case ODIN_ELEMENT_TYPE_FLOAT32: { float    v; memcpy(&v, p, 4); snprintf(buf, cap, "%g", (double)v); } break;
        case ODIN_ELEMENT_TYPE_FLOAT64: { double   v; memcpy(&v, p, 8); snprintf(buf, cap, "%g", v); } break;
        default:                        snprintf(buf, cap, "<%u B>", size); break;
    }
}

const char *ODIN_error_to_string(int error) {
    switch (error) {
        case ODIN_SUCCESS:
            return "Success";
        case ODIN_ERROR_NO_PARAMETER:
            return "No parameter";
        case ODIN_ERROR_PARAMETER_NOT_FOUND:
            return "Parameter not found";
        case ODIN_ERROR_SIZE_MISMATCH:
            return "Size mismatch";
        case ODIN_ERROR_PERMISSION_DENIED:
            return "Permission denied";
        case ODIN_ERROR_UNSUPPORTED_FORMAT:
            return "Unsupported format";
        case ODIN_ERROR_NOT_SUPPORTED:
            return "Not supported";
        case ODIN_ERROR_BUFFER_TOO_SMALL:
            return "Buffer too small";
        case ODIN_ERROR_INVALID_PARAMETER_ACTION:
            return "Invalid parameter action";
        case ODIN_ERROR:
            return "General error";
        default:
            return "Unknown error";
    }
}

// Recursively dump a composite (struct) value: each primitive field as
// "name: value", each nested CUSTOM field as a "name:" header followed by its
// own fields indented (via its descriptor's `nested` back-reference).
static void dump_composite(const ODIN_type_descriptor_t *td, const uint8_t *base, int depth,
                           printf_like_t printf_like, const void *context) {
    for (uint8_t i = 0; i < td->field_count; i++) {
        const ODIN_field_descriptor_t *f = &td->fields[i];
        if (f->nested) {
            printf_like(context, ANSI_CYN "%*s%s" ANSI_RESET ":\n", depth, "", f->name);
            dump_composite((const ODIN_type_descriptor_t *)f->nested, base + f->offset,
                           depth + 2, printf_like, context);
        } else {
            char val[64];
            dump_render_field(val, sizeof(val), f->element_type, base + f->offset, f->size);
            printf_like(context, ANSI_CYN "%*s%s" ANSI_RESET ": " ANSI_WHT "%s" ANSI_RESET "\n",
                        depth, "", f->name, val);
        }
    }
}

void ODIN_dump_parameter(const ODIN_parameter_t *parameter, int depth, odin_access_group_t access_group,
                         printf_like_t printf_like, const void *context) {
    // A scalar CUSTOM (struct) parameter — e.g. a <sensor>_reading — has no
    // string form, so encode_parameter_to_string renders it as "<N B struct>".
    // Expand it instead: walk its codegen-attached COMPOSITE field descriptor
    // and print each field's value (read from the live data buffer at its
    // offset). The sensor readings now become human-readable in the dump.
    if (parameter->element_type == ODIN_ELEMENT_TYPE_CUSTOM &&
        parameter->odin_type == ODIN_TYPE_PARAMETER && parameter->data) {
        const ODIN_extension_t *ext = find_extension(parameter, ODIN_EXTENSION_TYPE_COMPOSITE);
        if (ext && ext->data) {
            const ODIN_type_descriptor_t *td = (const ODIN_type_descriptor_t *)ext->data;
            printf_like(context, ANSI_CYN "%*s%s" ANSI_RESET ":\n", depth, "",
                        parameter->name_and_description);
            dump_composite(td, (const uint8_t *)parameter->data, depth + 2, printf_like, context);
            return;
        }
    }

    char str_buffer[512];
    int ret = ODIN_encode_parameter_to_string(parameter, str_buffer, sizeof(str_buffer), access_group);

    if (ret < 0) {
        ret = sprintf(str_buffer, "Error: %s", ODIN_error_to_string(ret));
    }

    printf_like(context, ANSI_CYN "%*s%s" ANSI_RESET ": " ANSI_WHT "%s" ANSI_RESET "\n", depth, "", parameter->name_and_description, str_buffer);
}

void ODIN_dump_recursive_tree(const ODIN_parameter_group_t *group, int depth, odin_access_group_t access_group,
                              printf_like_t printf_like, const void *context) {
    for (int i = 0; i < group->count; i++) {
        const ODIN_parameter_generic_t *parameter = (ODIN_parameter_generic_t *)group->parameters[i];

        switch (parameter->odin_type) {
            case ODIN_TYPE_PARAMETER:
            case ODIN_TYPE_ARRAY:
            case ODIN_TYPE_VECTOR: {
                const ODIN_parameter_t *subparameter = (ODIN_parameter_t *)group->parameters[i];
                ODIN_dump_parameter(subparameter, depth, access_group, printf_like, context);
            } break;

            case ODIN_TYPE_GROUP: {
                const ODIN_parameter_group_t *sub_group = (ODIN_parameter_group_t *)group->parameters[i];
                printf_like(context,"%*s" ANSI_GRN "[%s]" ANSI_RESET "\n", depth, "", sub_group->name_and_description);
                ODIN_dump_recursive_tree(sub_group, depth + 2, access_group, printf_like, context);

            } break;
        }
    }
}