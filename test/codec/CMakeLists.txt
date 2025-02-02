
# Create a test executable
add_executable(test_codec OD.c test_codec.cpp)

target_link_libraries(test_codec PRIVATE gtest gtest_main odin)
target_include_directories(test_codec PRIVATE ${CMAKE_SOURCE_DIR})


add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c ${CMAKE_CURRENT_SOURCE_DIR}/OD.h
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR} --advanced
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)
