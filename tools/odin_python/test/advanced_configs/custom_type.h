#include "extensions/extensions.h"
typedef struct {
    float r;
    float g;
    float b;
} rgb_color_t;
extern ODIN_string_serialisation_extension_ops_t rgb_color_serialiser;