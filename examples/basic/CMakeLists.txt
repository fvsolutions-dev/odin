add_executable(basic_example
    main.c
    OD.c
)

target_include_directories(basic_example PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
# Link against the library
target_link_libraries(basic_example PRIVATE odin)