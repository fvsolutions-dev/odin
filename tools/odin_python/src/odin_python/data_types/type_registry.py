import re
import struct
from abc import ABC, abstractmethod
from math import e
from typing import Annotated, Any, Dict, List
from unittest.mock import Base

import csnake as cc
from pydantic import BaseModel, Field, PrivateAttr, RootModel

from odin_python.data_types.type_definition import DataTypeDefintion, TypeAndDefaultModel, TypeModel, TypeModelDefinitions


class DataType(BaseModel, ABC):
    typename: str
    c_typename: str = Field(description="The C typename that corresponds to the data type")
    py_typename: str = Field(description="The Python typename that corresponds to the data type")
    size: int = Field(description="Size of the data type in bytes")
    default: Any = Field(description="The default value for the data type")
    struct_format: str = Field(description="The python struct format string for the data type")

    @abstractmethod
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable: ...

    @abstractmethod
    def to_c_array_initialiser(self, name: str, defaults: Any, dimensions: List[int]) -> cc.Variable: ...

    def extra_extension(self) -> str | None:
        return None

    @property
    def python_primitive_typename(self) -> str:
        if isinstance(self, BuiltinDataType):
            return self.primtive
        else:
            return self.py_typename


class BuiltinDataType(DataType):
    primtive: str = Field(description="The python primitive type for the data type")

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, f"Default value must be provided, because {self.typename} does not provide a default value"
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(str(default)),  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=[cc.TextModifier(str(x)) for x in defaults],  # type: ignore
        )

    def to_python_struct(self) -> str:
        """Convert the data type to a python struct format string"""

        assert self.struct_format is not None, f"Python struct format string not defined for {self.typename}"

        return self.struct_format


class BooleanCDataType(BuiltinDataType):
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, "Default value must be provided"

        if default:
            value = "true"
        else:
            value = "false"

        return super().to_c_initialiser(name, value)

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        value = ["true" if x else "false" for x in defaults]

        return super().to_c_array_initialiser(name, value, dimensions)


class CharCDataType(BuiltinDataType):
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, "Default value must be provided"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(f"'{default}'"),  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any] | str | None, dimensions: List[int]) -> cc.Variable:
        if isinstance(defaults, str):
            value = cc.TextModifier(f'"{defaults}"')  # type: ignore
        elif defaults is None:
            value = [cc.TextModifier("0")]  # type: ignore
        else:
            value = [cc.TextModifier(f"'{x}'") for x in defaults]  # type: ignore
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=value,  # type: ignore
        )


class DataTypeModel(
    RootModel["list[DataType] | DataType"],
):
    pass

    def struct_format(self, depth: int) -> str:
        if isinstance(self.root, DataType):
            return self.root.struct_format
        elif isinstance(self.root, list):
            return "".join([x.struct_format for x in self.root])
        else:
            raise ValueError(f"Unknown type {self.root} for {self}")

    @property
    def default(self) -> Any:
        if isinstance(self.root, DataType):
            return self.root.default
        elif isinstance(self.root, list):
            return [x.default for x in self.root]
        else:
            raise ValueError(f"Unknown type {self.root} for {self}")

    def to_flat_dict(self, depth: int) -> Dict[str, DataType | list[DataType]]:
        """Convert the model to a flat list of type, will  flatten the model"""
        if isinstance(self.root, DataType):
            return {self.root.typename: self.root}
        elif isinstance(self.root, list):
            return {x.typename: x for x in self.root}

        else:
            raise ValueError(f"Unknown type {self.root} for {self}")


class DataTypeModelDefinition(BaseModel):
    root: (
        DataTypeModel
        | Dict[
            str,
            "DataTypeModel  | DataTypeModelDefinition",
        ]
    )
    is_referenced: bool = Field(description="Whether the model is referenced based on another model")
    is_custom: bool = Field(description="Whether the model is a custom type")

    @property
    def size(self) -> int:
        return struct.calcsize(self.struct_format(depth=0))

    @property
    def default(self) -> Any:
        if isinstance(self.root, DataTypeModel):
            return self.root.default
        if isinstance(self.root, dict):
            defaults = {}
            for key, value in self.root.items():
                if isinstance(value, DataTypeModel):
                    defaults[key] = value.default
                elif isinstance(value, DataTypeModelDefinition):
                    defaults[key] = value.default
                else:
                    raise ValueError(f"Unknown type {value} for {key}")
            return defaults

        else:
            raise ValueError(f"Unknown type {self.root} for {self}")

    def struct_format(self, depth: int) -> str:
        if isinstance(self.root, DataTypeModel):
            return self.root.struct_format(depth=depth)

        elif isinstance(self.root, dict):
            format = ""
            for key, value in self.root.items():
                if isinstance(value, DataTypeModel):
                    format += value.struct_format(depth=depth)
                elif isinstance(value, DataTypeModelDefinition):
                    if value.is_referenced and depth < 1 and value.is_custom:
                        format += f"{value.size}s"
                    else:
                        format += value.struct_format(depth=depth - 1)
                else:
                    raise ValueError(f"Unknown type {value} for {key}")
            return format

        else:
            raise ValueError(f"Unknown type {self.root} for {self}")

    def to_flat_dict(self, depth: int) -> dict[str, DataType | list[DataType]]:
        """Convert the model to a flat list of type, will  flatten the model"""

        assert isinstance(self.root, dict)

        result: dict[str, DataType | list[DataType]] = {}

        for key, value in self.root.items():
            if isinstance(value.root, DataTypeModel):
                if isinstance(value.root.root, list):
                    keys : list[DataType] = []
                    for i, sub_value in enumerate(value.root.root):
                        keys.append(sub_value)
                    
                    result[key] = keys # type: ignore

                else:
                    result[key] = value.root.root

            elif isinstance(value.root, dict):
                if depth > 0:
                    sub_results = value.to_flat_dict(depth=depth - 1)
                else:
                    sub_results = {key: value}
                for sub_key, sub_value in sub_results.items():
                    result[f"{key}_{sub_key}"] = sub_value
            else:
                raise ValueError(f"Unknown type {value} for {key}")

        return result


class CustomDataType(DataType):
    string_serialiser: str | None = Field(description="The string serialiser for the data type")
    model: DataTypeModelDefinition = Field(
        description="The model for the data type",
    )

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        if default is None:
            default = self.default

        assert default is not None, "Default value must be provided, either in the parameter or in the type definition"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=default,  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        assert isinstance(defaults, list), "Defaults must be a list"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=defaults,  # type: ignore
        )

    def extra_extension(self) -> str | None:
        return None


BASE_DATA_TYPES: List[DataType] = [
    BuiltinDataType(typename="u64", size=8, c_typename="uint64_t", struct_format="Q", py_typename="OdinU64", default=0, primtive="int"),
    BuiltinDataType(typename="u32", size=4, c_typename="uint32_t", struct_format="I", py_typename="OdinU32", default=0, primtive="int"),
    BuiltinDataType(typename="u16", size=2, c_typename="uint16_t", struct_format="H", py_typename="OdinU16", default=0, primtive="int"),
    BuiltinDataType(typename="u8", size=1, c_typename="uint8_t", struct_format="B", py_typename="OdinU8", default=0, primtive="int"),
    BuiltinDataType(typename="i64", size=8, c_typename="int64_t", struct_format="Q", py_typename="OdinI64", default=0, primtive="int"),
    BuiltinDataType(typename="i32", size=4, c_typename="int32_t", struct_format="I", py_typename="OdinI32", default=0, primtive="int"),
    BuiltinDataType(typename="i16", size=2, c_typename="int16_t", struct_format="H", py_typename="OdinI16", default=0, primtive="int"),
    BuiltinDataType(typename="i8", size=1, c_typename="int8_t", struct_format="B", py_typename="OdinI8", default=0, primtive="int"),
    BuiltinDataType(typename="f32", size=4, c_typename="float", struct_format="f", py_typename="OdinF32", default=0.0, primtive="float"),
    BuiltinDataType(typename="f64", size=8, c_typename="double", struct_format="d", py_typename="OdinF64", default=0.0, primtive="float"),
    BooleanCDataType(typename="bool", size=1, c_typename="bool", struct_format="?", py_typename="OdinBool", default=False, primtive="int"),
    CharCDataType(typename="char", size=1, c_typename="char", struct_format="c", py_typename="OdinChar", default="0", primtive="str"),
]


def to_datatype_model(
    type_registry: "TypeRegistry",
    type: Dict[
        str,
        "TypeAndDefaultModel | TypeModel  | TypeModelDefinitions",
    ]
    | TypeModel
    | TypeAndDefaultModel,
) -> DataTypeModelDefinition:
    """Convert a data type model to a data type"""

    if isinstance(type, TypeModel) or isinstance(type, TypeAndDefaultModel):
        if isinstance(type, TypeModel):
            type_value = type.root
        else:
            type_value = type.type

        if isinstance(type_value, str):
            # If the model is a string, we need to resolve it
            datatype = type_registry.find_type(type_value)
            return DataTypeModelDefinition(
                root=datatype,  # type: ignore
                is_referenced=True,
                is_custom=isinstance(datatype, CustomDataType),
            )

        elif isinstance(type_value, list):
            return DataTypeModelDefinition(root=[type_registry.find_type(x) for x in type_value], is_referenced=True, is_custom=False)  # type: ignore
        else:
            raise ValueError(f"Unknown type {type_value}")

    elif isinstance(type, dict):
        models = {}
        for type_value, value in type.items():
            if isinstance(value, TypeAndDefaultModel) or isinstance(value, TypeModel):
                models[type_value] = to_datatype_model(type_registry, value)
            elif isinstance(value, dict):
                models[type_value] = to_datatype_model(type_registry, value)
            elif isinstance(value, TypeModelDefinitions):
                models[type_value] = to_datatype_model(type_registry, value.root)
            else:
                raise ValueError(f"Invalid type {value} in model")

        return DataTypeModelDefinition(root=models, is_referenced=False, is_custom=False)
    else:
        raise ValueError(f"Unknown type {type}")


class TypeRegistry:
    """The type registry, us used to store datatypes, it allows adding custom types"""

    def __init__(self):
        self.types: Dict[str, DataType] = {}

    def register_custom_datatype(self, name: str, type: DataTypeDefintion):
        """Register a custom data type"""

        if name in self.types:
            raise ValueError(f"Type {name} already registered")

        model = to_datatype_model(self, type.model.root)

        # Create the custom data type
        custom_type = CustomDataType(
            typename=name,
            c_typename=type.c_typename if type.c_typename is not None else f"{name}_t",
            py_typename=type.py_typename if type.py_typename is not None else f"Odin{name.title().replace('_', '')}",
            size=model.size,
            default=model.default,
            struct_format=model.struct_format(depth=0),
            model=model,
            string_serialiser=type.string_serialiser,
        )

        # Register the custom data type
        self.register(custom_type)

    def register(self, type: DataType | List[DataType]):
        """Register a new type"""

        if isinstance(type, list):
            for t in type:
                self.register(t)
            return

        if type.typename in self.types:
            raise ValueError(f"Type {type.typename} already registered")

        self.types[type.typename] = type

    def find_type(self, name: str) -> DataType:
        """Get a type by name"""

        if name not in self.types:
            raise ValueError(f"Type {name} not found")

        return self.types[name]

    def __repr__(self):
        # Return a list of all type names
        return f"TypeRegistry({', '.join(self.types.keys())})"

    def __getitem__(self, item: str):
        """Get a type by name"""
        return self.find_type(item)

    def __iter__(self):
        """Iterate over the types in the registry"""
        return iter(self.types.items())
