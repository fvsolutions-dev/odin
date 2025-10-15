from odin_python.parameter.parameter import ArrayParameterModel, VectorParameterModel
from ...parameter import BaseParameterGroupModel, ParameterModel, ParameterGroupModel

from ...data_types.type_registry import CustomDataType, BuiltinDataType, DataType


def generate_class(name: str, model: BaseParameterGroupModel, tab_indent: int, parent_model: str) -> str:
    data = ""
    indent = "    " * tab_indent
    data += f"{indent}class {name}(BaseRootModel):\n"

    data += f"{indent}    class Model(ConfiguredBaseModel):\n"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            data += f"{indent}        {child_name}: {child._resolved_type.python_primitive_typename}\n"

        elif isinstance(child, ArrayParameterModel):
            # Special case for bytes
            if child._resolved_type.c_typename == "uint8_t":
                data += f"{indent}        {child_name}: bytes\n"
            else:
                data += f"{indent}        {child_name}: list[{child._resolved_type.python_primitive_typename}]\n"

        elif isinstance(child, VectorParameterModel):
            # Special case for string and bytes
            if child._resolved_type.c_typename == "char":
                data += f"{indent}        {child_name}: str\n"
            elif child._resolved_type.c_typename == "uint8_t":
                data += f"{indent}        {child_name}: bytes\n"
            else:
                data += f"{indent}        {child_name}: list[{child._resolved_type.python_primitive_typename}]\n"

        elif isinstance(child, ParameterGroupModel):
            # Camelcase
            class_child_name = child_name.title().replace("_", "")
            data += f"{indent}        {child_name}:  '{parent_model}.{class_child_name}.Model'\n"

        # Else add comment for missing type
        else:
            data += f"{indent}     #   {child_name}:  '{parent_model}.{child_name}' # {type(child)}\n"

    # if not items print ...
    data += f"{indent}        pass\n\n"

    children = {}
    for child_name, child in model.children.items():
        if isinstance(child, ParameterGroupModel):
            # Camelcase
            class_child_name = child_name.title().replace("_", "")

            # Generate the class
            data += "\n"
            data += generate_class(class_child_name, child, tab_indent + 1, f"{parent_model}.{class_child_name}")
            children[child_name] = f"self.{child_name}"

    data += f"{indent}    def __init__(self, interface: TemplateInterface):\n"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            data += f"{indent}        self.{child_name} = ODINEntry[{child._resolved_type.py_typename}](0x{child.global_id:08X}, cls={child._resolved_type.py_typename},interface=interface)\n"
        elif isinstance(child, ArrayParameterModel):
            if child._resolved_type.c_typename == "uint8_t":
                data += f"{indent}        self.{child_name} = ODINBytesEntry(0x{child.global_id:08X}, interface=interface,max_length={child.elements}, fixed_length=True)\n"
            else:
                data += f"{indent}        self.{child_name} = ODINArrayEntry[{child._resolved_type.py_typename}](0x{child.global_id:08X}, cls={child._resolved_type.py_typename},elements={child.elements},element_size={child._resolved_type.size},interface=interface)\n"
        elif isinstance(child, VectorParameterModel):
            if child._resolved_type.c_typename == "char":
                data += f"{indent}        self.{child_name} = ODINStringEntry(0x{child.global_id:08X}, interface=interface,max_length={child.max_elements})\n"
            elif child._resolved_type.c_typename == "uint8_t":
                data += f"{indent}        self.{child_name} = ODINBytesEntry(0x{child.global_id:08X}, interface=interface,max_length={child.max_elements},fixed_length=False)\n"
            else:
                data += f"{indent}        self.{child_name} = ODINVectorEntry[{child._resolved_type.py_typename}](0x{child.global_id:08X}, cls={child._resolved_type.py_typename},max_elements={child.max_elements},element_size={child._resolved_type.size},interface=interface)\n"

        children[child_name] = f"self.{child_name}"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterGroupModel):
            data += f"{indent}        self.{child_name} = self.{child_name.title().replace('_', '')}(interface)\n"

    data += f"{indent}        self._children = {{\n"
    for child_name, child in children.items():
        data += f"{indent}            '{child_name}': {child},\n"
    data += f"{indent}        }}\n"

    data += f"{indent}        super().__init__(interface)\n\n"

    # Read mehtod
    data += f"{indent}    async def read(self) -> Model:\n"
    data += f"{indent}        data = await self.read_all()\n"

    data += f"{indent}        return self.Model(\n"
    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel) or isinstance(child, ParameterGroupModel):
            data += f"{indent}            {child_name}=data['{child_name}'],\n"
        elif isinstance(child, ArrayParameterModel):
            data += f"{indent}            {child_name}=data['{child_name}'],\n"
        elif isinstance(child, VectorParameterModel):
            data += f"{indent}            {child_name}=data['{child_name}'],\n"

        # elif isinstance(child, ParameterGroupModel):
        # data += f"{indent}            {child_name}=data['{child_name}'].read(),\n"
        else:
            data += f"{indent}            # {child_name}: data['{child_name}'] # {type(child)}\n"
    data += f"{indent}        )\n"

    return data



def generate_basemodel_type(name: str, datatype: CustomDataType) -> str:
    output = f"""class {datatype.py_typename}(GenericModel,ConfiguredBaseModel):
"""
    resolved_types = datatype.model.to_flat_dict(depth=1)

    for sub_name, sub_datatype in resolved_types.items():
        if isinstance(sub_datatype.root, DataType):
            if isinstance(sub_datatype.root, BuiltinDataType):
                typename = sub_datatype.root.python_primitive_typename
            elif isinstance(sub_datatype.root, CustomDataType):
                typename = sub_datatype.root.py_typename
            else:
                raise ValueError(f"Unknown type {sub_datatype.root} for {sub_name}")

            if sub_datatype.elements == 1:
                output += f"    {sub_name}: {typename}\n"
            else:
                output += f"    {sub_name}: tuple[{','.join([typename] * sub_datatype.elements)}]\n"

        else:
            raise ValueError(f"Unknown type {sub_datatype} for {sub_name}")

    # Add the encode and decode methods, use struct
    #
    output += f"""
    def encode_to_bytes(self) -> bytes:
        packed_data = struct.pack(
            '{datatype.struct_format}',
"""
    for i, (name, sub_datatype) in enumerate(resolved_types.items()):
        # if isinstance(sub_datatype, list):
        #     for j in range(len(sub_datatype)):
        #         output += f"            self.{name}[{j}],\n"

        if isinstance(sub_datatype.root, CustomDataType):
            if sub_datatype.elements == 1:
                output += f"            {sub_datatype.root.py_typename}.encode_to_bytes(self.{name}),\n"
            else:
                for j in range(sub_datatype.elements):
                    output += f"            {sub_datatype.root.py_typename}.encode_to_bytes(self.{name}[{j}]),\n"
        else:
            if sub_datatype.elements == 1:
                output += f"            self.{name},\n"
            else:
                output += f"            *self.{name},\n"
                
    output += f"""
        )
        return packed_data

    @classmethod
    def decode_from_bytes(cls, data: bytes) -> "{datatype.py_typename}":
        unpacked_data = struct.unpack('{datatype.struct_format}', data)
        return cls(
"""

    i = 0
    for name, sub_datatype in resolved_types.items():
        if isinstance(sub_datatype.root, CustomDataType):
            if sub_datatype.elements == 1:
                output += f"            {name}={sub_datatype.root.py_typename}.decode_from_bytes(unpacked_data[{i}]),\n"
                i += 1
            else:
                output += f"            {name}=(\n"
                for j in range(sub_datatype.elements):
                    output += f"                {sub_datatype.root.py_typename}.decode_from_bytes(unpacked_data[{i}]),\n"
                    i += 1
                output += "            ),\n"

        elif isinstance(sub_datatype.root, BuiltinDataType):
            if sub_datatype.elements > 1:
                output += f"            {name}=unpacked_data[{i}:{i + sub_datatype.elements}],\n"
                i += sub_datatype.elements
            else:
                output += f"            {name}=unpacked_data[{i}],\n"
                i += 1
        else:
            raise ValueError(f"Unknown type {sub_datatype} for {name}")

    output += """
        )

"""

    return output


def generate_standard_type(name: str, type_class: BuiltinDataType) -> str:
    python_type = type_class.python_primitive_typename
    format_string = type_class.to_python_struct()
    type_name = type_class.py_typename

    data = f"""class {type_name}(GenericModel,{python_type}):
    def encode_to_bytes(self) -> bytes:
        return struct.pack(
            '<{format_string}',
            self,
        )

    @classmethod
    def decode_from_bytes(cls, data: bytes) -> "{type_name}":
        return cls(
            *struct.unpack('<{format_string}', data)
        )

"""
    return data
