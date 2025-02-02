
# Create a test executable
add_executable(test_custom_type OD.c custom_type.c test_custom_type.cpp)

target_link_libraries(test_custom_type PRIVATE gtest gtest_main odin)
target_include_directories(test_custom_type PRIVATE ${CMAKE_SOURCE_DIR})

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c ${CMAKE_CURRENT_SOURCE_DIR}/OD.h
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR} --advanced
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)



