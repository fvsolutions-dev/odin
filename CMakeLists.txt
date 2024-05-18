
idf_component_register(SRCS "odin_datastore.c"
                            "odin/encode_protobuf.c"
                            "odin/encode_string.c"
                            "odin/odin.pb.c"
                            "odin/stdio_dump.c"
                            "odin/extensions.c"
                            INCLUDE_DIRS "."
                            REQUIRES nanopb srv_logging)