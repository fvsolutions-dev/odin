
#include "encoding/encode_string.h"
#include "odin.h"
#include "odin_utils.h"
#include <OD.h>
#include <stdio.h>
#include <string.h>

// format value as string

int main() {
  printf("Hello, World!\n");

  char buffer[256] = {0};
  int len = ODIN_encode_to_string(&root.u32_variable_length_array, buffer,
                                  sizeof(buffer), 0);

  printf("len: %d\n", len);
  printf("buffer: %s\n", buffer);

  // float test_float = 0.0;

  // int size = ODIN_parameter_read(&root.test_variable_float32, &test_float,
  // sizeof(test_float), 0);

  // printf("size: %d\n", size);
  // printf("test_float: %f\n", test_float);

  ODIN_dump_recursive_tree(&odin_store, 0);

  printf("Finish!\n");

  return 1;
}