import time

from odin_db import OdinDBModel, OdinDBParameterGroupModel, OdinDBParameterModel, OdinDBTypeDefinitionModel
from odin_db.models import ODINDBModelType

from odin_python.data_types.type_registry import CustomDataType, StardardDataType, TypeRegistry
from odin_python.loader import ParameterGroupModel
from odin_python.parameter import (
    RootParameterModel,
)
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


class ODIN_DB_generator:
    @staticmethod
    def generate_single_source(model: RootParameterModel, types: TypeRegistry) -> str:
        params = parameter_group_to_db(model)

        # Create repetable hash of the configuration
        import hashlib

        hash = hashlib.md5()
        hash.update(params.model_dump_json().encode("utf-8"))

        db_types: dict[str, OdinDBTypeDefinitionModel] = {}
        for name, defined_type in types:
            if not isinstance(defined_type, CustomDataType):
                continue

            type = type_to_db(defined_type)
            if type is None:
                continue
            db_types[name] = type
            
        db_model = OdinDBModel(
            name="ODIN",
            description="TODO",
            creation_timestamp=time.time(),
            configuration_hash=int(hash.hexdigest(), 16),
            root=parameter_group_to_db(model),
            types=db_types,
        )

        return db_model.model_dump_json(indent=4)
