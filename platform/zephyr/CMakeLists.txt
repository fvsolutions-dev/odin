zephyr_library_named(odin)
zephyr_library_sources(
    "../../src/odin_core.c"
    "../../src/codec/TLV_codec.c"
    "../../src/codec/string_codec.c"
    "../../src/codec/number_codec.c"
#    "../../src/codec/json_codec.c" Not needed for now
#    "../../src/codec/protobuff_codec.c" Not needed for now
    "../../src/extensions/validate_extension.c"
    "../../src/extensions/io_extension.c"
    "../../src/extensions/extensions.c"
    "../../src/odin_utils.c"
    "../../src/odin_security.c"
    "../../src/odin_lookup.c"
)

target_include_directories(odin PUBLIC ../../src)

