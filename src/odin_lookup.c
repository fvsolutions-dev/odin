#include "odin_lookup.h"

#include "odin.h"

const ODIN_parameter_generic_t *ODIN_get_generic_parameter_by_id(const ODIN_parameter_group_t *group, uint32_t index,
                                                                 uint32_t parent_shift) {
    if (group == NULL) {
        return NULL;
    }
    
    int shift = group->shift + parent_shift;

    uint32_t mask = ((1 << shift) - 1) << (32 - shift);
    for (int parameter_idx = 0; parameter_idx < group->count; parameter_idx++) {
        ODIN_parameter_generic_t *parameter = (ODIN_parameter_generic_t *)group->parameters[parameter_idx];

        // Check if the mask matches
        if ((parameter->global_index & mask) != (index & mask)) {
            continue;
        }

        // If we have an exact match, return the parameter
        if (parameter->global_index == index) {
            return parameter;
        }

        // If the parameter is a group, we need to check the children of the group
        if (parameter->odin_type == ODIN_TYPE_GROUP) {
            return ODIN_get_generic_parameter_by_id((ODIN_parameter_group_t *)parameter, index, shift);
        }
    }
    return NULL;
}

const ODIN_parameter_t *ODIN_get_parameter_by_id(const ODIN_parameter_group_t *group, uint32_t index, uint32_t parent_shift) {
    const ODIN_parameter_generic_t *parameter = ODIN_get_generic_parameter_by_id(group, index, parent_shift);
    if (parameter == NULL) {
        return NULL;
    }
    if (parameter->odin_type == ODIN_TYPE_GROUP) {
        return NULL;
    }

    return (ODIN_parameter_t *)parameter;
}

const ODIN_parameter_group_t *ODIN_get_parameter_group_by_id(const ODIN_parameter_group_t *group, uint32_t index,
                                                             uint32_t parent_shift) {
    const ODIN_parameter_generic_t *parameter = ODIN_get_generic_parameter_by_id(group, index, parent_shift);
    if (parameter == NULL) {
        return NULL;
    }
    if (parameter->odin_type != ODIN_TYPE_GROUP) {
        return NULL;
    }

    return (ODIN_parameter_group_t *)parameter;
}
