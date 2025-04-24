from ...parameter import BaseParameterGroupModel, ParameterModel, ParameterGroupModel
from ...data_types.type_registry import CustomDataType, StandardDataType


# class RootModel(BaseRootModel):
#     class Model(BaseModel):
#         raw_sensor_data: "RootModel.RawSensorData.Model"

#     class RawSensorData(BaseRootModel):
#         class Model(BaseModel):
#             BMI323_1: OdinTimestampedvec7
#             BMI323_2: OdinTimestampedvec7
#             BMI323_3: OdinTimestampedvec7
#             BMI323_4: OdinTimestampedvec7
#             ADIS16607_1: OdinTimestampedvec7
#             ADIS16607_2: OdinTimestampedvec7
#             LIS3MDL_1: OdinTimestampedvec3
#             ADXL1001_1: OdinTimestampedvec1


#         def __init__(self, interface: TemplateInterface):
#             self.BMI323_1 = ODINEntry[OdinTimestampedvec7](0xE0B10000, cls=OdinTimestampedvec7,interface=interface)
#             self.BMI323_2 = ODINEntry[OdinTimestampedvec7](0xE0B20000, cls=OdinTimestampedvec7,interface=interface)
#             self.BMI323_3 = ODINEntry[OdinTimestampedvec7](0xE0B30000, cls=OdinTimestampedvec7,interface=interface)
#             self.BMI323_4 = ODINEntry[OdinTimestampedvec7](0xE0B40000, cls=OdinTimestampedvec7,interface=interface)
#             self.ADIS16607_1 = ODINEntry[OdinTimestampedvec7](0xE0A10000, cls=OdinTimestampedvec7,interface=interface)
#             self.ADIS16607_2 = ODINEntry[OdinTimestampedvec7](0xE0A20000, cls=OdinTimestampedvec7,interface=interface)
#             self.LIS3MDL_1 = ODINEntry[OdinTimestampedvec3](0xE0C00000, cls=OdinTimestampedvec3,interface=interface)
#             self.ADXL1001_1 = ODINEntry[OdinTimestampedvec1](0xE0A00000, cls=OdinTimestampedvec1,interface=interface)
#             self._children = {
#                 'BMI323_1': self.BMI323_1,
#                 'BMI323_2': self.BMI323_2,
#                 'BMI323_3': self.BMI323_3,
#                 'BMI323_4': self.BMI323_4,
#                 'ADIS16607_1': self.ADIS16607_1,
#                 'ADIS16607_2': self.ADIS16607_2,
#                 'LIS3MDL_1': self.LIS3MDL_1,
#                 'ADXL1001_1': self.ADXL1001_1,
#             }
#             super().__init__(interface)

#         async def read(self) -> Model:
#             data = await self.read_all()

#             return self.Model(
#                 BMI323_1=data['BMI323_1'],
#                 BMI323_2=data['BMI323_2'],
#                 BMI323_3=data['BMI323_3'],
#                 BMI323_4=data['BMI323_4'],
#                 ADIS16607_1=data['ADIS16607_1'],
#                 ADIS16607_2=data['ADIS16607_2'],
#                 LIS3MDL_1=data['LIS3MDL_1'],
#                 ADXL1001_1=data['ADXL1001_1'],
#             )


def generate_class(name: str, model: BaseParameterGroupModel, tab_indent: int, parent_model: str) -> str:
    data = ""
    indent = "    " * tab_indent
    data += f"{indent}class {name}(BaseRootModel):\n"

    data += f"{indent}    class Model(BaseModel):\n"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            resolved_type = child._resolved_type
            assert isinstance(resolved_type, StandardDataType)
            data += f"{indent}        {child_name}: {odin_type_to_python_type(resolved_type.typename)}\n"

        elif isinstance(child, ParameterGroupModel):
            # Camelcase
            class_child_name = child_name.title().replace("_", "")
            data += f"{indent}        {child_name}:  '{parent_model}.{class_child_name}.Model'\n"
        # Else add comment for missing type
        else:
            data += f"{indent}     #   {child_name}:  '{parent_model}.{child_name}' # {type(child)}\n"

    # if not items print ...
    data += f"{indent}        pass\n"

    childds = {}
    for child_name, child in model.children.items():
        if isinstance(child, ParameterGroupModel):
            # Camelcase
            class_child_name = child_name.title().replace("_", "")

            # Generate the class
            data += "\n"
            data += generate_class(class_child_name, child, tab_indent + 1, f"{parent_model}.{class_child_name}")
            childds[child_name] = f"self.{child_name}"

    data += f"{indent}    def __init__(self, interface: TemplateInterface):\n"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            resolved_type = child._resolved_type
            assert isinstance(resolved_type, StandardDataType)
            # type = resolved_type.py_typename
            # if isinstance(resolved_type, CustomDataType):
            data += f"{indent}        self.{child_name} = ODINEntry[{get_pyton_type_name(resolved_type.typename)}](0x{child.global_id:08X}, cls={get_pyton_type_name(resolved_type.typename)},interface=interface)\n"
            # else:
            # data += f"{indent}        self.{child_name} = ODINEntry[{type}.BASE_TYPE](0x{child.global_id:08X}, cls={type})\n"
            childds[child_name] = f"self.{child_name}"

    for child_name, child in model.children.items():
        if isinstance(child, ParameterGroupModel):
            data += f"{indent}        self.{child_name} = self.{child_name.title().replace('_', '')}(interface)\n"

    data += f"{indent}        self._children = {{\n"
    for child_name, child in childds.items():
        data += f"{indent}            '{child_name}': {child},\n"
    data += f"{indent}        }}\n"

    data += f"{indent}        super().__init__(interface)\n"

    # Read mehtod
    data += f"{indent}    async def read(self) -> Model:\n"
    data += f"{indent}        data = await self.read_all()\n"

    data += f"{indent}        return self.Model(\n"
    for child_name, child in model.children.items():
        if isinstance(child, ParameterModel):
            data += f"{indent}            {child_name}=data['{child_name}'],\n"
        elif isinstance(child, ParameterGroupModel):
            data += f"{indent}            {child_name}=data['{child_name}'].read(),\n"
        else:
            data += f"{indent}            # {child_name}: data['{child_name}'] # {type(child)}\n"
    data += f"{indent}        )\n"

    return data


def odin_type_to_python_type(odin_type: str) -> str:
    """Convert an ODIN type to a Python type"""
    if odin_type == "bool":
        return "int"
    elif odin_type in ["u8", "u16", "u32", "u64", "i8", "i16", "i32", "i64"]:
        return "int"
    elif odin_type in ["f32", "f64"]:
        return "float"
    elif odin_type in ["char"]:
        return "str"
    else:
        return get_pyton_type_name(odin_type)


def get_pyton_type_name(odin_type: str) -> str:
    # camelcase with odin prefix
    return "Odin" + odin_type.title().replace("_", "")


def generate_custom_type(name: str, type_class: CustomDataType) -> str:
    if type_class.model is None:
        print(f"Model for {name} is not defined")
        return ""

    # assert type_class.resolved_model is not None, "Model must be resolved before generating class"

    type_name = get_pyton_type_name(type_class.typename)

    data = f"""class {type_name}(GenericModel,BaseModel):
"""
    resolved_types = type_class.model.to_flat_dict().items()

    for name, data_type in resolved_types:
        if isinstance(data_type, list):
            data += f"    {name}: tuple["
            for i in range(len(data_type)):
                data += f"{odin_type_to_python_type(data_type[i].typename)}, "

            data = data[:-2]  # remove the last comma and space
            data += f"]\n"

        elif isinstance(data_type, StandardDataType):
            data += f"    {name}: {odin_type_to_python_type(data_type.typename)}\n"
        else:
            raise ValueError(f"Unknown type {data_type} for {name}")

    # Add the encode and decode methods, use struct
    #
    data += f"""
    def encode_to_bytes(self) -> bytes:
        packed_data = struct.pack(
            '{type_class.to_python_struct()}',
"""

    for i, (name, data_type) in enumerate(resolved_types):
        if isinstance(data_type, list):
            for j in range(len(data_type)):
                data += f"            self.{name}[{j}],\n"

        elif isinstance(data_type, CustomDataType):
            data += f"            {get_pyton_type_name(data_type.typename)}.encode_to_bytes(self.{name}),\n"
        else:
            data += f"            self.{name},\n"

    data += f"""
        )
        return packed_data

    @classmethod
    def decode_from_bytes(cls, data: bytes) -> "{type_name}":
        unpacked_data = struct.unpack('{type_class.to_python_struct()}', data)
        return cls(
"""
    i = 0
    for name, data_type in resolved_types:
        if isinstance(data_type, list):
            data += f"            {name}=("
            for j in range(len(data_type)):
                data += f"unpacked_data[{i + j}], "

            data = data[:-2]  # remove the last comma and space
            data += "),\n"
            i += len(data_type)

        elif isinstance(data_type, CustomDataType):
            data += (
                f"            {name}={get_pyton_type_name(data_type.typename)}.decode_from_bytes(unpacked_data[{i}]),\n"
            )
            i += 1
        elif isinstance(data_type, StandardDataType):
            data += f"            {name}=unpacked_data[{i}],\n"
            i += 1
        else:
            raise ValueError(f"Unknown type {data_type} for {name}")

    data += """
        )

"""

    return data


def generate_standard_type(name: str, type_class: StandardDataType) -> str:
    python_type = odin_type_to_python_type(type_class.typename)
    format_string = type_class.to_python_struct()
    type_name = get_pyton_type_name(type_class.typename)

    data = f"""class {type_name}(GenericModel,{python_type}):
    def encode_to_bytes(self) -> bytes:
        return struct.pack(
            '{format_string}',
            self,
        )

    @classmethod
    def decode_from_bytes(cls, data: bytes) -> "{type_name}":
        return cls(
            *struct.unpack('{format_string}', data)
        )

"""
    return data
