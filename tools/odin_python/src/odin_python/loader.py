from typing import Dict

from pydantic import BaseModel, Field, RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as


from odin_python.data_types.type_model import TypeDefinitionsModel
from odin_python.parameter import (
    ArrayParameterModel,
    ParameterGroupModel,
    ParameterModel,
    VectorParameterModel,
    AccessControlCollection,
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
