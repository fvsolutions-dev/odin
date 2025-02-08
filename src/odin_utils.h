#include <stddef.h>

#include "odin.h"
#include "odin_security.h"

const char *ODIN_error_to_string(int error);
void ODIN_dump_parameter(const ODIN_parameter_t *parameter, int depth, odin_access_group_t access_group);
void ODIN_dump_recursive_tree(const ODIN_parameter_group_t *group, int depth, odin_access_group_t access_group);
