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
    EXPECT_EQ(ODIN_parameter_write(&odin_objects.validate_variable, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_VALIDATION_ERROR);

    data = -100000.0;
    EXPECT_EQ(ODIN_parameter_write(&odin_objects.validate_variable, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_VALIDATION_ERROR);

    data = 0.0;
    EXPECT_GE(ODIN_parameter_write(&odin_objects.validate_variable, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_SUCCESS);
}

TEST(ODINExtensions, NominalReference) {
    odin_variables.validate_variable = 0;

    float data = 21.0;
    EXPECT_GE(ODIN_parameter_write(&odin_objects.referenced_variable, &data, sizeof(data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_SUCCESS);

    EXPECT_NEAR(odin_variables.validate_variable, (data - 1.0) / 5.0, 0.0001);


    // Read value
    float read_data;
    EXPECT_GE(ODIN_parameter_read(&odin_objects.referenced_variable, &read_data, sizeof(read_data), ODIN_ACCESS_GROUP_INTERNAL),
              ODIN_SUCCESS);

    EXPECT_NEAR(read_data, data, 0.0001);

}
