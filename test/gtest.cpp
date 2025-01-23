#include <gtest/gtest.h>

// extern "C" {
//     #include "my_c_code.h" // Include your C code
// }

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

TEST(MyCodeTests, AddFunctionTest) {
    EXPECT_EQ(add(2, 3), 5); // Replace with your actual C function
}

TEST(MyCodeTests, SubtractFunctionTest) {
    EXPECT_EQ(subtract(5, 3), 2); // Replace with your actual C function
}