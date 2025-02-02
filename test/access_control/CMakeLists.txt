
# Create a test executable
add_executable(access_control_tests OD.c test_access_control.cpp)

target_link_libraries(access_control_tests PRIVATE gtest gtest_main odin)
target_include_directories(access_control_tests PRIVATE ${CMAKE_SOURCE_DIR})


add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c ${CMAKE_CURRENT_SOURCE_DIR}/OD.h
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR} --advanced
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)
