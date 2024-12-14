from typing import Dict

from odin_python.parameter.parameter import (
    ArrayParameterModel,
    ParameterModel,
    ParameterGroupModel,
    ReferenceParameterModel,
    VectorParameterModel,
)
from pydantic import RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as



class LoaderModel(
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
