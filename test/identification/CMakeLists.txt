
# Create a test executable
add_executable(identification_test OD.c test_identification.cpp)

target_link_libraries(identification_test PRIVATE gtest gtest_main odin)
target_include_directories(identification_test PRIVATE ${CMAKE_SOURCE_DIR})

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR} --advanced
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)



