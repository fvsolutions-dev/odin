cmake_minimum_required(VERSION 3.15...3.26)

# Sources that build cleanly without external proto/json dependencies. The
# protobuf and json codecs need nanopb / extra deps and are intentionally left
# out of the host and ESP-IDF builds.
set(ODIN_CORE_SRCS
    src/odin_c/odin_core.c
    src/odin_c/codec/TLV_codec.c
    src/odin_c/codec/string_codec.c
    src/odin_c/codec/number_codec.c
    src/odin_c/extensions/validate_extension.c
    src/odin_c/extensions/io_extension.c
    src/odin_c/extensions/extensions.c
    src/odin_c/odin_utils.c
    src/odin_c/odin_security.c
    src/odin_c/odin_lookup.c
)
set(ODIN_INCLUDE_DIR src/odin_c)

# Remember where the repo lives so odin_generate_c() can fall back to
# `uv run --directory <repo>` when the `odin` CLI is not on PATH (typical for
# ESP-IDF builds that have not sourced the project venv).
set(ODIN_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "Odin repo root")

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

    set(_odin_gen_c "${ODIN_GEN_OUTPUT_DIR}/${ODIN_GEN_NAME}.c")
    set(_odin_gen_h "${ODIN_GEN_OUTPUT_DIR}/${ODIN_GEN_NAME}.h")

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

    set(ODIN_GEN_C           "${_odin_gen_c}"            PARENT_SCOPE)
    set(ODIN_GEN_H           "${_odin_gen_h}"            PARENT_SCOPE)
    set(ODIN_GEN_SOURCES     "${_odin_gen_c}" "${_odin_gen_h}" PARENT_SCOPE)
    set(ODIN_GEN_INCLUDE_DIR "${ODIN_GEN_OUTPUT_DIR}"    PARENT_SCOPE)
endfunction()

# If ESP-IDF is reading this CMakeLists.txt, register it as an ESP-IDF component
if(DEFINED ENV{IDF_PATH})
  idf_component_register(
      SRCS ${ODIN_CORE_SRCS}
      INCLUDE_DIRS ${ODIN_INCLUDE_DIR}
  )
  return()
endif()

# If Zephyr is reading this CMakeLists.txt, register it as a Zephyr module
if(Zephyr_FOUND)
  zephyr_library_named(odin)
  zephyr_library_sources(${ODIN_CORE_SRCS})
  target_include_directories(odin PUBLIC ${ODIN_INCLUDE_DIR})
  return()
endif()

# Otherwise: standalone host build (Linux / macOS / Windows). This is what the
# C tests link against — no FreeRTOS / nanopb required.
project(odin VERSION 1.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Coverage")
    if(CMAKE_C_COMPILER_ID MATCHES "Clang")
        set(_COV_FLAGS -fprofile-instr-generate -fcoverage-mapping)
    else()
        set(_COV_FLAGS --coverage)
    endif()
    add_compile_options(${_COV_FLAGS})
    add_link_options(${_COV_FLAGS})
endif()

enable_testing()

add_library(odin STATIC ${ODIN_CORE_SRCS})
target_include_directories(odin PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/${ODIN_INCLUDE_DIR})

add_subdirectory(test)
