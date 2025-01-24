add_library(odin STATIC
    odin_core.c
    encoding/encode_string.c
    odin_utils.c
    odin_security.c
)

# Expose the src directory as the include path for public headers
target_include_directories(odin PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# (Optional) Set compiler options
# target_compile_options(odin PRIVATE -Wall -Wextra -O2)