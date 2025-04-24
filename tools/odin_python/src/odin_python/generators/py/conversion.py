from ...parameter import BaseParameterGroupModel, ParameterModel, ParameterGroupModel
from ...data_types.type_registry import StandardDataType


def generate_class(name: str, model: BaseParameterGroupModel, tab_indent: int = 0) -> str:
    data = ""
    indent = "    " * tab_indent
    data += f"{indent}class {name}(BaseRootModel):\n"
    data += f"{indent}    def __init__(self, interface):\n"

    childds = {}
    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            resolved_type = child._resolved_type
            assert isinstance(resolved_type, StandardDataType)

            type = resolved_type.py_typename

            data += f"{indent}        self.{child_name} = ODINEntry[{type}.BASE_TYPE](0x{child.global_id:08X}, cls={type})\n"
            childds[child_name] = f"self.{child_name}"

        elif isinstance(child, ParameterGroupModel):
            # Camelcase
            class_child_name = child_name.title().replace("_", "")

            # Generate the class
            data += "\n"
            data += generate_class(class_child_name, child, tab_indent + 2)
            data += f"{indent}        self.{child_name} = {class_child_name}(interface)\n"
            childds[child_name] = f"self.{child_name}"

    data += f"{indent}        self._children = {{\n"
    for child_name, child in childds.items():
        data += f"{indent}            '{child_name}': {child},\n"
    data += f"{indent}        }}\n"

    data += f"{indent}        super().__init__(interface)\n"

    return data
