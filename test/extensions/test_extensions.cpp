#include <gtest/gtest.h>
#include <stdint.h>

extern "C" {
#include "OD.h"
#include "odin.h"
#include "odin_codec.h"
#include "odin_core.h"
#include "odin_lookup.h"
}

TEST(ODINExtensions, NominalValidation) {
    float data = 100000.0;
    EXPECT_EQ(ODIN_parameter_write(&root.base_variable_float, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_VALIDATION_ERROR);
    
    data = -100000.0;
    EXPECT_EQ(ODIN_parameter_write(&root.base_variable_float, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_VALIDATION_ERROR);
    
    data = 0.0;
    EXPECT_GE(ODIN_parameter_write(&root.base_variable_float, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL), ODIN_SUCCESS);

}
