
from odin_python.loader import ParameterGroupModel
from odin_python.parameter import (
    RootParameterModel,
)
from odin_python.parameter.parameter import BaseParameterGroupModel, ParameterModel

from odin_python.data_types.type_registry import RegularCDataType


class PYGenerator:
    @staticmethod
    def generate_class(name: str, model: BaseParameterGroupModel, tab_indent: int = 0) -> str:
        data = ""
        # 
        indent = "    " * tab_indent
        data += f"{indent}class {name}(BaseRootModel):\n"

        data += f"{indent}    def __init__(self, interface):\n"

        childds = {}
        for child_name, child in model.children.items():
            if isinstance(child, ParameterModel):
                resolved_type = child._resolved_type
                assert isinstance(resolved_type, RegularCDataType)

                type = resolved_type.py_typename

                data += f"{indent}        self.{child_name} = ODINEntry[{type}.BASE_TYPE](0x{child.global_id:08X}, cls={type})\n"
                childds[child_name] = f"self.{child_name}"
            elif isinstance(child, ParameterGroupModel):
                # Camelcase
                class_child_name = child_name.title().replace("_", "")

                # Generate the class
                data += PYGenerator.generate_class(class_child_name, child, tab_indent + 2)
                data += f"{indent}        self.{child_name} = {class_child_name}(interface)\n"
                childds[child_name] = f"self.{child_name}"

        data += f"{indent}        self._children = {{\n"
        for child_name, child in childds.items():
            data += f"{indent}            '{child_name}': {child},\n"
        data += f"{indent}        }}\n"

        data += f"{indent}        super().__init__(interface)\n"

        return data

    @staticmethod
    def generate_lib(model: RootParameterModel) -> str:
        # return model.dump_json()
        # iterate trough top level children
        data  =""
        data += "from odin_python.py_generator.entry import BaseRootModel, ODINBaseEntry, ODINEntry, OdinBool, OdinF32, OdinI32\n\n"
        data += PYGenerator.generate_class("RootModel", model, 0)
        return data

    #         data += "class RootModel():\n"
    #         for name,child in model.children.items():
    #             if isinstance(child, ParameterModel):
    #                 # data += f"    {name} = {child.default}\n"
    # #     test_float = ODINEntry[float](id=0x0A010000, cls=Float32)
    #                 data += f"    {name} = ODINEntry[{child.type}](0x{child.global_id:08X}, cls={child.type})\n"
    #             else:
    #                 data += f"    {name}"
    # return data

    @staticmethod
    def generate_single_source(model: RootParameterModel) -> str:
        return PYGenerator.generate_lib(model)
