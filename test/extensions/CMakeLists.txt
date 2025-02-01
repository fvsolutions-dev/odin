
# Create a test executable
add_executable(extensions_test OD.c test_extensions.cpp)

target_link_libraries(extensions_test PRIVATE gtest gtest_main odin)
target_include_directories(extensions_test PRIVATE ${CMAKE_SOURCE_DIR})

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR} --advanced
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)



