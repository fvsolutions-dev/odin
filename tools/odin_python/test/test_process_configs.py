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

import subprocess

import pytest
import glob


CONFIGS = glob.glob("test/configs/*.yaml")


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


def process_config(config: str):
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model = LoaderModel.from_yaml( config)

    root_parameters = RootParameterModel(children=model.root)  # type: ignore
    root_parameters.post_load_resolve(None, "root", registry)

    # 
    with open(f"{config}.c", "w") as f:
        f.write(CGenerator.generate_single_source(root_parameters))

    return f"{config}.c"

def compile_file(file: str):
    command = f"clang -o {file}.o -c {file} -I D:/Projects/odin_datastore/odin/tools/odin_python/test/configs -L /usr/local/lib"
    print(command)
    e = subprocess.run(command, shell=True)
    if e.returncode != 0:
        raise Exception(f"Failed to compile {file}")

# Parameterize with all the configs
@pytest.mark.parametrize("config", CONFIGS)
def test_basic_parse(config: str):
    file = process_config(config)
    compile_file(file)
    
if __name__ == "__main__":
    for config in CONFIGS:
        print(f"processing {config}")
        file = process_config(config)
        compile_file(file)
        