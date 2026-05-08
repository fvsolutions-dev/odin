# odin_generate_c(YAML <file> [NAME <name>] [OUTPUT_DIR <dir>])
#
# Runs the `odin` Python CLI at build time to turn a parameter YAML into
# <NAME>.c / <NAME>.h. Outputs sit in the build tree by default so they are
# never committed. The function exports the following variables to its caller:
#   ODIN_GEN_C            full path to the generated .c file
#   ODIN_GEN_H            full path to the generated .h file
#   ODIN_GEN_SOURCES      both of the above as a list
#   ODIN_GEN_INCLUDE_DIR  directory holding the generated header
#
# The codegen command can be overridden with -DODIN_CODEGEN_COMMAND=<cmd...>.
#
# This file is included separately by every consumer (top-level CMakeLists.txt
# AND each ESP-IDF component CMakeLists.txt) because ESP-IDF's
# component_get_requirements phase runs each component file in an isolated
# `cmake -P` invocation — functions defined in sibling components are NOT
# visible there.

include_guard(GLOBAL)

# Repo root is one directory up from this file (cmake/OdinCodegen.cmake → repo).
get_filename_component(_odin_repo_root "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(ODIN_REPO_ROOT "${_odin_repo_root}" CACHE INTERNAL "Odin repo root")

function(odin_generate_c)
    cmake_parse_arguments(ODIN_GEN "" "YAML;NAME;OUTPUT_DIR" "" ${ARGN})

    if(NOT ODIN_GEN_YAML)
        message(FATAL_ERROR "odin_generate_c: YAML argument is required")
    endif()
    if(NOT IS_ABSOLUTE "${ODIN_GEN_YAML}")
        set(ODIN_GEN_YAML "${CMAKE_CURRENT_SOURCE_DIR}/${ODIN_GEN_YAML}")
    endif()
    if(NOT ODIN_GEN_NAME)
        set(ODIN_GEN_NAME "OD")
    endif()
    if(NOT ODIN_GEN_OUTPUT_DIR)
        set(ODIN_GEN_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/odin_generated")
    endif()

    set(_odin_gen_c "${ODIN_GEN_OUTPUT_DIR}/${ODIN_GEN_NAME}.c")
    set(_odin_gen_h "${ODIN_GEN_OUTPUT_DIR}/${ODIN_GEN_NAME}.h")

    # ESP-IDF's idf_component_register asserts that every INCLUDE_DIRS entry
    # exists at configure time. The codegen only runs at build time, so create
    # the output directory now to satisfy that check.
    file(MAKE_DIRECTORY "${ODIN_GEN_OUTPUT_DIR}")

    # Always export the paths so callers can plumb them into the consuming
    # target (e.g. idf_component_register SRCS / INCLUDE_DIRS).
    set(ODIN_GEN_C           "${_odin_gen_c}"            PARENT_SCOPE)
    set(ODIN_GEN_H           "${_odin_gen_h}"            PARENT_SCOPE)
    set(ODIN_GEN_SOURCES     "${_odin_gen_c}" "${_odin_gen_h}" PARENT_SCOPE)
    set(ODIN_GEN_INCLUDE_DIR "${ODIN_GEN_OUTPUT_DIR}"    PARENT_SCOPE)

    # add_custom_command / set_source_files_properties are not allowed in
    # script mode (`cmake -P`), which is what ESP-IDF uses for its
    # component_get_requirements phase. The function gets called again during
    # the real configure pass, where these commands will register correctly.
    if(CMAKE_SCRIPT_MODE_FILE)
        return()
    endif()

    if(NOT ODIN_CODEGEN_COMMAND)
        find_program(ODIN_CLI_EXE odin)
        if(ODIN_CLI_EXE)
            set(ODIN_CODEGEN_COMMAND "${ODIN_CLI_EXE}")
        else()
            find_program(UV_EXE uv)
            if(UV_EXE)
                set(ODIN_CODEGEN_COMMAND
                    "${UV_EXE}" run --directory "${ODIN_REPO_ROOT}" odin)
            else()
                message(FATAL_ERROR
                    "odin_generate_c: neither 'odin' nor 'uv' found on PATH. "
                    "Run 'uv sync' in ${ODIN_REPO_ROOT} and re-run cmake, or "
                    "pass -DODIN_CODEGEN_COMMAND=<cmd> to point at a working "
                    "odin CLI.")
            endif()
        endif()
    endif()

    add_custom_command(
        OUTPUT "${_odin_gen_c}" "${_odin_gen_h}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${ODIN_GEN_OUTPUT_DIR}"
        COMMAND ${ODIN_CODEGEN_COMMAND} generate
                "${ODIN_GEN_YAML}" "${ODIN_GEN_OUTPUT_DIR}"
                --name "${ODIN_GEN_NAME}" --target C
        DEPENDS "${ODIN_GEN_YAML}"
        COMMENT "odin: generating ${ODIN_GEN_NAME}.c/.h from ${ODIN_GEN_YAML}"
        VERBATIM
    )

    set_source_files_properties("${_odin_gen_c}" "${_odin_gen_h}"
        PROPERTIES GENERATED TRUE)
endfunction()
