cmake_minimum_required(VERSION 3.10)
project(ODIN VERSION 1.0 LANGUAGES C)

set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)

# Set default build type to Release
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Add the library
add_subdirectory(src)

# Add example projects
add_subdirectory(examples)

# (Optional) Add unit tests
# enable_testing()
# add_subdirectory(tests)