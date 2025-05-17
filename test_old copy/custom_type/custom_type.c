#include "custom_type.h"

#include <stdio.h>

#include "extensions/extensions.h"
#include "odin.h"

static int to_string(const struct ODIN_parameter *parameter, const void *data, size_t size, char *buffer, size_t buffer_size) {
    sprintf(buffer, "rgb_color_t{r=%.2f, g=%.2f, b=%.2f}", ((rgb_color_t *)data)->r, ((rgb_color_t *)data)->g,
            ((rgb_color_t *)data)->b);

    return 0;
}

ODIN_string_serialisation_extension_ops_t rgb_color_serialiser = {
    .to_string = to_string,
};
