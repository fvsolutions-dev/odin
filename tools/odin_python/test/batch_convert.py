import os
from typing import Dict

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generator.generate_c import (
    CGenerator,
)
from odin_python.parameter.parameter import (
    ParameterGroupModel,
    ParameterModel,
    RootParameterModel,
)
from pydantic import RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as
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


CONFIGS = [
    r"basic\config.yaml",
    r"reference\config.yaml",
    r"array\arrays.yaml",
]


def process_config(config: str):
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model = LoaderModel.from_yaml(os.path.join(os.path.dirname(__file__), config))

    root_parameters = RootParameterModel(children=model.root)  # type: ignore
    root_parameters.post_load_resolve(None, "root", registry)

    escaped_name = config.replace("\\", "_")
    
    with open(f"test_generated_{escaped_name}.c", "w") as f:
        f.write(CGenerator.generate_single_source(root_parameters))


if __name__ == "__main__":
    for config in CONFIGS:
        process_config(config)
