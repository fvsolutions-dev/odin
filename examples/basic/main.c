
#include <OD.h>
#include <stdio.h>
#include <string.h>

#include "encoding/encode_string.h"
#include "odin.h"
#include "odin_utils.h"

int main() {
    printf("Hello, World!\n");

    char buffer[256] = {0};
    int len = ODIN_encode_to_string(&root.u32_array, buffer, sizeof(buffer), 0);

    printf("len: %d\n", len);
    printf("buffer: %s\n", buffer);

    ODIN_dump_recursive_tree(&odin_store, 0);

    printf("Finish!\n");

    return 1;
}