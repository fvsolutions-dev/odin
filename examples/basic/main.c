
#include "encoding/encode_string.h"
#include "odin.h"
#include "odin_utils.h"
#include <OD.h>
#include <stdio.h>
#include <string.h>

void dump_tree(const ODIN_parameter_group_t *group, int depth) {
  for (int i = 0; i < group->count; i++) {
    ODIN_parameter_generic_t *parameter =
        (ODIN_parameter_generic_t *)group->parameters[i];

    switch (parameter->odin_type) {
    case ODIN_TYPE_PARAMETER: 
    case ODIN_TYPE_ARRAY: 
    case ODIN_TYPE_VECTOR: 
    {
      ODIN_parameter_t *parameter = (ODIN_parameter_t *)group->parameters[i];
      uint8_t data[256];
      char buffer[256] = {0};
      int ret = ODIN_encode_to_string(parameter, buffer, sizeof(buffer), 0);
      if (ret < 0) {
        printf("Error: %s\n", ODIN_error_to_string(ret));
        continue;
      }

      printf("%*s%s: %s\n", depth, "", parameter->name_and_description, buffer);
    } break;

    case ODIN_TYPE_GROUP: {
      ODIN_parameter_group_t *parameter =
          (ODIN_parameter_group_t *)group->parameters[i];
      printf("%*s%s\n", depth, "", parameter->name_and_description);
      dump_tree(parameter, depth + 2);
    } break;
    }
  }
}

// format value as string

int main() {
  printf("Hello, World!\n");

  char buffer[256] = {0};
  int len = ODIN_encode_to_string(&root.u32_variable_length_array, buffer, sizeof(buffer), 0);

  printf("len: %d\n", len);
  printf("buffer: %s\n", buffer);

  // float test_float = 0.0;

  // int size = ODIN_parameter_read(&root.test_variable_float32, &test_float,
  // sizeof(test_float), 0);

  // printf("size: %d\n", size);
  // printf("test_float: %f\n", test_float);
  sizeof(root);
  sizeof(root_ram);
  
  dump_tree(&odin_store, 0);

  printf("Finish!\n");

  return 1;
}