from typing import Dict

from pydantic import BaseModel, Field, RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as


from odin_python.data_types.type_registry import CustomDataType, DataType, TypeRegistry
from odin_python.parameter import (
    ArrayParameterModel,
    ParameterGroupModel,
    ParameterModel,
    ReferenceParameterModel,
    VectorParameterModel,
    AccessControlCollection,
)


class SimpleLoaderModel(
    RootModel[
        Dict[
            str,
            ParameterModel
            | ParameterGroupModel
            | ReferenceParameterModel
            | ArrayParameterModel
            | VectorParameterModel,
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


class TypeModel(BaseModel):
    typename: str
    string_serialiser: str


class TypeDefinitions(RootModel[Dict[str, TypeModel]]):
    @classmethod
    def empty(cls):
        return TypeDefinitions(root={})

    def register_types(self, registry: TypeRegistry):
        for type_name, type_model in self.root.items():
            registry.register(
                CustomDataType(
                    typename=type_name,
                    c_typename=type_model.typename,
                    size=0,
                    string_serialiser=type_model.string_serialiser,
                )
            )


class AdvancedLoaderModel(BaseModel):
    access_control: AccessControlCollection = Field(
        default_factory=AccessControlCollection.empty,
        description="Access control for the parameters",
    )
    c_include: list[str] = Field(
        default_factory=list,
        description="List of extra C includes",
    )

    types: TypeDefinitions = Field(
        default_factory=TypeDefinitions.empty,
        description="Type definitions",
    )

    parameters: Dict[
        str,
        ParameterModel
        | ParameterGroupModel
        | ReferenceParameterModel
        | ArrayParameterModel
        | VectorParameterModel,
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
