
# Enable testing
enable_testing()

# Force GoogleTest to use the dynamic runtime library
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add GoogleTest
add_subdirectory(${CMAKE_SOURCE_DIR}/../googletest ${CMAKE_BINARY_DIR}/googletest)

# Add your test executable
add_executable(tests gtest.cpp)
add_executable(basic_test basic/basic_test.cpp ${CMAKE_SOURCE_DIR}/test/basic/OD.c)

target_link_libraries(tests PRIVATE gtest gtest_main odin)
target_link_libraries(basic_test PRIVATE gtest gtest_main odin)

target_include_directories(tests PRIVATE ${CMAKE_SOURCE_DIR})
target_include_directories(basic_test PRIVATE ${CMAKE_SOURCE_DIR})

# Add custom command to generate config.yaml
add_custom_command(
    OUTPUT ${CMAKE_SOURCE_DIR}/test/basic/OD.c
    COMMAND odin gen-c ${CMAKE_SOURCE_DIR}/test/basic/config.yaml ${CMAKE_SOURCE_DIR}/test/basic
    DEPENDS ${CMAKE_SOURCE_DIR}/test/basic/config.yaml
)
# add_dependencies(basic_test ${CMAKE_BINARY_DIR}/output.cpp)

# Make it a dependency of the basic_test target
# add_custom_target(generate_config_yaml DEPENDS ${CMAKE_SOURCE_DIR}/examples/basic/config.yaml)

# Add the custom target as a dependency of the basic_test target
# add_dependencies(basic_test generate_config_yaml)