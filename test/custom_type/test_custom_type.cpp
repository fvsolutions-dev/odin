#include <gtest/gtest.h>
#include <stdint.h>

extern "C" {
#include "OD.h"
#include "odin.h"
#include "odin_codec.h"
#include "odin_core.h"
#include "odin_lookup.h"
}

TEST(ODINCustomType, NominalReadWrite) {

    // Read custom value
    rgb_color_t color = {};
    EXPECT_GE(ODIN_parameter_read(&odin_objects.rgb_color, &color, sizeof(color), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);
    EXPECT_EQ(color.r, odin_variables.rgb_color.r);
    EXPECT_EQ(color.g, odin_variables.rgb_color.g);
    EXPECT_EQ(color.b, odin_variables.rgb_color.b);

    // Write value
    rgb_color_t new_color = {.r = 1, .g = 2, .b = 3};
    EXPECT_GE(ODIN_parameter_write(&odin_objects.rgb_color, &new_color, sizeof(new_color), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_SUCCESS);
    EXPECT_EQ(new_color.r, odin_variables.rgb_color.r);
    EXPECT_EQ(new_color.g, odin_variables.rgb_color.g);
    EXPECT_EQ(new_color.b, odin_variables.rgb_color.b);


    // Create string
    char buffer[100] = {};
    EXPECT_GE(ODIN_encode_parameter_to_string(&odin_objects.rgb_color, buffer, sizeof(buffer), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_SUCCESS);
    printf("Buffer: %s\n", buffer);

}
