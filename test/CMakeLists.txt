
# Enable testing
enable_testing()

# Force GoogleTest to use the dynamic runtime library
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add GoogleTest
add_subdirectory(${CMAKE_SOURCE_DIR}/../googletest ${CMAKE_BINARY_DIR}/googletest)

add_subdirectory(access_control)
add_subdirectory(basic_config)
add_subdirectory(codec)
add_subdirectory(identification)

