odin_generate_c(YAML odin.yaml NAME OD)

idf_component_register(
    SRCS "main.c" ${ODIN_GEN_C}
    INCLUDE_DIRS "." ${ODIN_GEN_INCLUDE_DIR}
    REQUIRES odin
)
