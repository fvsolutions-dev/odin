add_executable(basic_example
    main.c
    ${CMAKE_CURRENT_SOURCE_DIR}/OD.c
)

target_include_directories(basic_example PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
# Link against the library
target_link_libraries(basic_example PRIVATE odin)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/OD.c ${CMAKE_CURRENT_SOURCE_DIR}/OD.h
    COMMAND odin gen-c ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.yaml
)
