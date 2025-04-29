from math import e
from turtle import st
from odin_db import ODINDBModelType, OdinDBParameterGroupModel, OdinDBParameterModel, OdinDBTypeDefinitionModel

from ...data_types.type_registry import CustomDataType, DataType, DataTypeModel, DataTypeModelDefinition
from ...parameter import BaseParameterGroupModel, ParameterGroupModel, ParameterModel


def parameter_to_db(parameter: ParameterModel) -> OdinDBParameterModel:
    return OdinDBParameterModel(
        name=parameter._name,
        description=parameter.resolved_description,
        global_id=parameter.global_id,
        global_name=parameter.global_name,
        size=parameter._resolved_type.size,
        element_type=parameter._resolved_type.typename,
    )


def parameter_group_to_db(group: BaseParameterGroupModel) -> OdinDBParameterGroupModel:
    parameters = []
    for name, child in group.children.items():
        if isinstance(child, ParameterModel):
            parameters.append(parameter_to_db(child))
        elif isinstance(child, ParameterGroupModel):
            parameters.append(parameter_group_to_db(child))

    return OdinDBParameterGroupModel(
        name=group._name,
        global_name=group.global_name,
        description=group.resolved_description,
        parameters=parameters,
    )


def datatypemodel_to_dict(data_type: DataTypeModel) -> list[ ODINDBModelType] | ODINDBModelType:

    if isinstance(data_type.root, list):
        output : list[OdinDBTypeDefinitionModel | ODINDBModelType] = []

        for i, child in enumerate(data_type.root):
            if isinstance(child, CustomDataType):
                output.append(type_to_db(child.model))
            elif isinstance(child, DataType):
                output.append(ODINDBModelType.from_string(child.typename))
            else:
                raise ValueError(f"Unknown data type: {child}")
        return output
    
    elif isinstance(data_type.root, DataType):
        if isinstance(data_type.root, CustomDataType):
            return type_to_db(data_type.root.model)
        elif isinstance(data_type.root, DataType):
            return ODINDBModelType.from_string(data_type.root.typename)
        else:
            raise ValueError(f"Unknown data type: {data_type.root}")
            # structure_items["__base__"] = ODINDBModelType.from_string(data_type.root.typename)
    else:
        raise ValueError(f"Unknown data type: {data_type.root}")
    
    # return structure_items


def type_to_db(type: DataTypeModelDefinition) -> OdinDBTypeDefinitionModel | ODINDBModelType:
    structure_items: dict[str, OdinDBTypeDefinitionModel | ODINDBModelType] = {}
    print("WARNING: type_to_db is commented out")

    if isinstance(type.root, dict):
        for name, child in type.root.items():
            if isinstance(child, DataTypeModel):
                structure_items[name] = datatypemodel_to_dict(child)

            elif isinstance(child, DataTypeModelDefinition):
                structure_items[name] = type_to_db(child)

                # if isinstance(child.root, CustomDataType):
                #     structure_items[name] = type_to_db(child.root)
                # else:
                #     structure_items[name] = ODINDBModelType.from_string(child.root.typename)

            #     structure_items[name] = type_to_db(child)
            # else:
            #     structure_items[name] = ODINDBModelType.from_string(child.typename)

    elif isinstance(type.root, DataTypeModel):
        structure_items = datatypemodel_to_dict(type.root)
    else:
        raise ValueError(f"Unknown data type: {type.root}")
    
    return OdinDBTypeDefinitionModel(
        size=type.size,
        structure=structure_items,
    )
