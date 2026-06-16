set(UNITY_DIR "$ENV{UNITY_DIR}" CACHE PATH "Path to Unity test framework")
if(NOT UNITY_DIR)
    set(UNITY_DIR "/opt/Unity" CACHE PATH "" FORCE)
endif()

if(NOT EXISTS "${UNITY_DIR}/src/unity.c")
    message(FATAL_ERROR
        "Unity not found at ${UNITY_DIR}. "
        "Set UNITY_DIR to a Unity checkout, or rebuild the devcontainer to "
        "populate /opt/Unity.")
endif()

function(odin_add_unity_test name source)
    add_executable(${name} ${source} ${UNITY_DIR}/src/unity.c)
    target_include_directories(${name} PRIVATE ${UNITY_DIR}/src)
    target_link_libraries(${name} PRIVATE odin)
    add_test(NAME ${name} COMMAND ${name})
    set_tests_properties(${name} PROPERTIES TIMEOUT 30)
endfunction()

odin_add_unity_test(security_test     c/security_test.c)
odin_add_unity_test(parameter_test    c/parameter_test.c)
odin_add_unity_test(lookup_test       c/lookup_test.c)
odin_add_unity_test(string_codec_test c/string_codec_test.c)
