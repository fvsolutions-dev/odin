
idf_component_register(SRCS "../../../src/odin_core.c"
    "../../../src/codec/TLV_codec.c"
    "../../../src/codec/protobuff_codec.c"
    "../../../src/codec/string_codec.c"
    "../../../src/codec/number_codec.c"
    "../../../src/codec/json_codec.c"
    "../../../src/extensions/validate_extension.c"
    "../../../src/extensions/io_extension.c"
    "../../../src/extensions/extensions.c"
    "../../../src/odin_utils.c"
    "../../../src/odin_security.c"
    "../../../src/odin_lookup.c"

    INCLUDE_DIRS "../../../src"
    REQUIRES "main")
