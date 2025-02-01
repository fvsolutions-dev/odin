from typing import Dict

from pydantic import BaseModel, Field, RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as


from odin_python.parameter import (
    ArrayParameterModel,
    ParameterGroupModel,
    ParameterModel,
    ReferenceParameterModel,
    VectorParameterModel,
    AccessControlCollection
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


class AdvancedLoaderModel(BaseModel):
    access_control: AccessControlCollection = Field(
        default_factory=AccessControlCollection.empty,
        description="Access control for the parameters",
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
