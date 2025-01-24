from typing import Dict, List

from pydantic import BaseModel, Field, RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generator.generate_c import (
    CGenerator,
)
from odin_python.parameter.access_control import (
    AccesControlCollection,
    AccesControlEntry,
)
from odin_python.parameter.parameter import (
    ArrayParameterModel,
    ParameterGroupModel,
    ParameterModel,
    ReferenceParameterModel,
    RootParameterModel,
    VectorParameterModel,
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
    access_control: AccesControlCollection = Field(
        default_factory=AccesControlCollection.empty,
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
