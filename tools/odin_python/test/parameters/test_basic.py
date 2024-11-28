from typing import Dict

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.parameter.parameter import ParameterModel
from pydantic import RootModel
from pydantic_yaml import parse_yaml_file_as
import csnake as cc  # type: ignore
from odin_python.utils.csnake_custom import StructVariable


CONFIG = r"test\parameters\1_regular_parameter.yaml"


class LoaderModel(RootModel[Dict[str, ParameterModel]]):
    @classmethod
    def from_yaml(cls, file_path: str):
        return parse_yaml_file_as(cls, file_path)

    def dump_json(self):
        return self.model_dump_json(indent=2)

    def dump_summary(self):
        for value in self.root.values():
            print(value.one_line_summary())

    def resolve_types(self, type_registry: TypeRegistry):
        for name, param in self.root.items():
            param.post_load_resolve(None, name, type_registry)

    def to_c_odin_parameter_initialiser(self) -> cc.Variable:
        return cc.Variable(
            name="self.parameter_name",
            primitive="self.odin_c_type",
            value={
                group_name: group.to_c_odin_parameter_initialiser().value
                for group_name, group in self.root.items()  # type: ignore
            },
        )

    def to_recursive_odin_typedef(self) -> cc.Struct:
        struct = StructVariable("odin_c_type", typedef=True)

        # Create the data structures for groups
        for child in self.root.values():
            struct.add_variable(child.to_c_odin_parameter_initialiser())

        return struct


def test_basic_parse():
    model = LoaderModel.from_yaml(CONFIG)
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model.resolve_types(registry)

    print(model.dump_json())
    print(model.dump_summary())

    cw = cc.CodeWriter()
    cw.add_struct(model.to_recursive_odin_typedef())

    cw.add_variable_initialization(model.to_c_odin_parameter_initialiser())

    file = str(cw)
    print(file)


if __name__ == "__main__":
    test_basic_parse()
