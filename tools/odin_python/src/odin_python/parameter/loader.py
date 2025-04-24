from typing import Dict, Literal

from pydantic import BaseModel, Field, RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as

from ..data_types.type_model import TypeDefinitionsModel
from ..data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from ..generators.abstract_generator import ModelContext
from .parameter import (
    AccessControlCollection,
    ArrayParameterModel,
    ParameterGroupModel,
    ParameterModel,
    RootParameterModel,
    VectorParameterModel,
)


class SimpleLoaderModel(
    RootModel[
        Dict[
            str,
            ParameterModel | ParameterGroupModel | ArrayParameterModel | VectorParameterModel,
        ]
    ]
):
    @classmethod
    def from_yaml(cls, file_path: str):
        try:
            return parse_yaml_file_as(cls, file_path)
        except ValidationError as validation_error:
            print(validation_error.errors())
            for error in validation_error.errors():
                print(error["loc"])
                print(error["msg"])

            raise Exception("Failed to parse yaml file")


class AdvancedLoaderModel(BaseModel):
    access_control: AccessControlCollection = Field(
        default_factory=AccessControlCollection.empty,
        description="Access control for the parameters",
    )
    c_include: list[str] = Field(
        default_factory=list,
        description="List of extra C includes",
    )

    types: TypeDefinitionsModel = Field(
        default_factory=TypeDefinitionsModel.empty,
        description="Type definitions",
    )
    groups: Dict[str, list[str]] = Field(
        default_factory=dict,
        description="Groups of parameters",
    )
    parameters: Dict[
        str,
        ParameterModel | ParameterGroupModel | ArrayParameterModel | VectorParameterModel,
    ]
    id_space_shift: int = Field(description="ID space shift for the parameters")

    @classmethod
    def from_yaml(cls, file_path: str):
        try:
            return parse_yaml_file_as(cls, file_path)
        except ValidationError as validation_error:
            print(validation_error.errors())
            for error in validation_error.errors():
                print(error["loc"])
                print(error["msg"])

            raise Exception("Failed to parse yaml file")


class ConfigurationReader:
    def __init__(self):
        pass

    def load(self, file_path: str, type: Literal["simple", "advanced"]) -> ModelContext:
        registry = TypeRegistry()
        registry.register(BASE_DATA_TYPES)

        try:
            if type == "simple":
                model = SimpleLoaderModel.from_yaml(file_path)

                root_parameters = RootParameterModel(
                    children=model.root,
                    id_space_shift=8,
                )

            elif type == "advanced":
                model = AdvancedLoaderModel.from_yaml(file_path)
                model.types.register_types(registry)

                root_parameters = RootParameterModel(
                    children=model.parameters,
                    access_control=model.access_control,
                    id_space_shift=model.id_space_shift,
                )

            else:
                raise ValueError("Invalid type. Use 'simple' or 'advanced'.")

            root_parameters.post_load_resolve(None, "root", registry)

            return ModelContext(
                root_model=root_parameters,
                types=registry,
            )

        except ValidationError as validation_error:
            print(validation_error.errors())
            for error in validation_error.errors():
                print(error["loc"])
                print(error["msg"])

            raise Exception("Failed to parse yaml file")
