#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "ansi_colors.h"
#include "odin_datastore.h"
#include "encode_string.h"
#include "stdio_dump.h"

#define MAX_VALUE_LENGTH 128

void ODIN_dump(ODIN_store_t *OD, bool compact, uint16_t access_group)
{
    for (int i = 0; i < OD->count; i++)
    {
        ODIN_dump_parameter_group(OD->groups[i], compact, access_group);
    }
}

void ODIN_dump_parameter_group(ODIN_parameter_group_t *group, bool compact, uint16_t access_group)
{
    if (group == NULL)
    {
        return;
    }
    printf(ANSI_BMAG "Group: '%s'" ANSI_RESET "\n", group->name);

    for (int i = 0; i < group->count; i++)
    {
        ODIN_dump_parameter(group->parameters[i], compact, access_group);
    }
}

void ODIN_dump_parameter(ODIN_parameter_t *parameter, bool compact, uint16_t access_group)
{
    if (parameter == NULL)
    {
        return;
    }

    char buffer[MAX_VALUE_LENGTH];
    int len = ODIN_read_as_string(parameter, buffer, sizeof(buffer), access_group);
    if (len <= 0)
    {
        printf("Error: %s\n", ODIN_error_to_string(len));
        return;
    }

    if (compact)
    {
        printf(" %-25s: %s\n", parameter->name, buffer);
    }
    else
    {
        printf("Parameter: '" ANSI_BCYN "%s" ANSI_RESET "'\n", parameter->name);
        printf("Value:     %s\n", buffer);
        printf("Data:      %p\n", parameter->data);
        printf("Size:      %d\n", parameter->size);
        printf("Access:    %04X\n", parameter->access);
        if (parameter->description != NULL)
            printf("Description:\n" ANSI_BLK "%s" ANSI_RESET "\n", parameter->description);
    }
}

void ODIN_log_parameter_access(ODIN_parameter_t *parameter, const char *operation, uint16_t access_group)
{
    if (parameter == NULL)
    {
        return;
    }

    char buffer[MAX_VALUE_LENGTH];
    int len = ODIN_read_as_string(parameter, buffer, sizeof(buffer), access_group);
    if (len <= 0)
    {
        sprintf(buffer, "Error");
    }

    printf(ANSI_BMAG "%s: %s = %s" ANSI_RESET "\n", operation, parameter->name, buffer);
}
