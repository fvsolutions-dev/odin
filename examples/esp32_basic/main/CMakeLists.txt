# ESP-IDF runs each component's CMakeLists.txt in isolation during the
# component_get_requirements phase, so we cannot rely on functions defined in
# the odin component being visible here. Include the helper directly.
include(${CMAKE_CURRENT_LIST_DIR}/../../../cmake/OdinCodegen.cmake)

odin_generate_c(YAML odin.yaml NAME OD)

idf_component_register(
    SRCS "main.c" ${ODIN_GEN_C}
    INCLUDE_DIRS "." ${ODIN_GEN_INCLUDE_DIR}
    REQUIRES odin
)
