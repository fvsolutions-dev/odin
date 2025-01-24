
# Enable testing
enable_testing()

# Force GoogleTest to use the dynamic runtime library
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add GoogleTest
add_subdirectory(${CMAKE_SOURCE_DIR}/../googletest ${CMAKE_BINARY_DIR}/googletest)

# Create a test executable
add_executable(tests ${CMAKE_SOURCE_DIR}/test/basic_config/OD.c
                    basic_config/write_tests.cpp 
                    basic_config/read_tests.cpp 
                    basic_config/array_tests.cpp
                    basic_config/test_security.cpp
                    )
target_link_libraries(tests PRIVATE gtest gtest_main odin)
target_include_directories(tests PRIVATE ${CMAKE_SOURCE_DIR})

# Add custom command to generate config.yaml
add_custom_command(
    OUTPUT ${CMAKE_SOURCE_DIR}/test/basic_config/OD.c
    COMMAND odin gen-c ${CMAKE_SOURCE_DIR}/test/basic_config/config.yaml ${CMAKE_SOURCE_DIR}/test/basic_config
    DEPENDS ${CMAKE_SOURCE_DIR}/test/basic_config/config.yaml
)