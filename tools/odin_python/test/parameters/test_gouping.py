from typing import Dict

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generator.generate_c import (
    CGenerator,
)
from odin_python.parameter.parameter import (
    ParameterModel,
    ParameterGroupModel,
    RootParameterModel,
)
from pydantic import RootModel, ValidationError
from pydantic_yaml import parse_yaml_file_as
import csnake as cc  # type: ignore


CONFIG = r"test\parameters\2_group_parameter.yaml"


class LoaderModel(RootModel[Dict[str, ParameterModel | ParameterGroupModel]]):
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


def test_basic_parse():
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model = LoaderModel.from_yaml(CONFIG)
    root_parameters = RootParameterModel(children=model.root)
    root_parameters.post_load_resolve(None, "root", registry)

    print(root_parameters.dump_json())
    print(root_parameters.one_line_summary())

    cw = cc.CodeWriter()
    cw.add_line("")
    cw.add_struct(root_parameters.to_recursive_odin_typedef(type_name="root_type_t"))
    cw.add_line("")
    cw.add_variable_initialization(
        root_parameters.to_c_odin_parameter_initialiser(
            param_name="root", type_name="root_type_t"
        )
    )
    file = str(cw)
    print(file)

    # Save to to a test file
    with open("test.c", "w") as f:
        f.write(file)


def test_basic_generated():
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model = LoaderModel.from_yaml(CONFIG)

    root_parameters = RootParameterModel(children=model.root)
    root_parameters.post_load_resolve(None, "root", registry)

    with open("test_generated.c", "w") as f:
        f.write(CGenerator.generate_source(root_parameters))
    with open("test_generated.h", "w") as f:
        f.write(CGenerator.generate_header(root_parameters))


if __name__ == "__main__":
    test_basic_parse()
    test_basic_generated()
