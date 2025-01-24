
# Create a test executable
add_executable(basic_config_tests OD.c
                     write_tests.cpp 
                     read_tests.cpp 
                     array_tests.cpp
                     test_security.cpp)

target_link_libraries(basic_config_tests PRIVATE gtest gtest_main odin)
target_include_directories(basic_config_tests PRIVATE ${CMAKE_SOURCE_DIR})

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)



