from odin_db import OdinDBParameterGroupModel, OdinDBParameterModel, OdinDBTypeDefinitionModel
from odin_db.models import ODINDBModelType

from odin_python.data_types.type_registry import CustomDataType
from odin_python.loader import ParameterGroupModel
from odin_python.parameter.parameter import BaseParameterGroupModel, ParameterModel


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


def type_to_db(type: CustomDataType) -> OdinDBTypeDefinitionModel | None:
    structure_items = {}

    if type.resolved_model is None:
        print(f"Type {type.typename} has no resolved model")
        return None

    for name, child in type.resolved_model.items():
        if isinstance(child, CustomDataType):
            structure_items[name] = type_to_db(child)
        else:
            structure_items[name] = ODINDBModelType.from_string(child.typename)

    return OdinDBTypeDefinitionModel(
        size=type.size,
        structure=structure_items,
    )
