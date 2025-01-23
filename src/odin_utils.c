#include <stdio.h>

#include "encoding/encode_string.h"
#include "odin.h"
#include "ansi_colors.h"

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

        case ODIN_ERROR:
            return "General error";
        default:
            return "Unknown error";
    }
}

void ODIN_dump_recursive_tree(const ODIN_parameter_group_t *group, int depth) {
    uint8_t value_buffer[256];
    char str_buffer[256];

    for (int i = 0; i < group->count; i++) {
        ODIN_parameter_generic_t *parameter = (ODIN_parameter_generic_t *)group->parameters[i];

        switch (parameter->odin_type) {
            case ODIN_TYPE_PARAMETER:
            case ODIN_TYPE_ARRAY:
            case ODIN_TYPE_VECTOR: {
                ODIN_parameter_t *parameter = (ODIN_parameter_t *)group->parameters[i];
                int ret = ODIN_encode_to_string(parameter, str_buffer, sizeof(str_buffer), 0);
                if (ret < 0) {
                    ret = sprintf(str_buffer, "Error: %s", ODIN_error_to_string(ret));
                }

                printf("%*s"ANSI_CYN"%s"ANSI_RESET": "ANSI_BLK"%s"ANSI_RESET"\n", depth, "", parameter->name_and_description, str_buffer);
            } break;

            case ODIN_TYPE_GROUP: {
                ODIN_parameter_group_t *parameter = (ODIN_parameter_group_t *)group->parameters[i];
                printf("%*s"ANSI_GRN"[%s]"ANSI_RESET"\n", depth, "", parameter->name_and_description);
                ODIN_dump_recursive_tree(parameter, depth + 4);

            } break;
        }
    }
}