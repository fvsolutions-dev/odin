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

# odin_generate_c() helper. Defined in cmake/OdinCodegen.cmake so consumers
# (e.g. example main components) can include it directly without depending on
# this top-level file having been processed first — necessary because ESP-IDF's
# component_get_requirements phase loads each component CMakeLists.txt in
# isolation.
include(${CMAKE_CURRENT_LIST_DIR}/cmake/OdinCodegen.cmake)

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
