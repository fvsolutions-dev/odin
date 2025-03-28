#include <stdint.h>
#include <stdbool.h>
#include "odin.h"

void ODIN_dump(const ODIN_store_t *OD, bool compact, uint16_t access_group);
void ODIN_dump_parameter(const ODIN_parameter_t *parameter, bool compact, uint16_t access_group);
void ODIN_dump_parameter_group(const ODIN_parameter_group_t *group, bool compact, uint16_t access_group);
void ODIN_log_parameter_access(const ODIN_parameter_t *parameter, const char *operation, uint16_t access_group);
