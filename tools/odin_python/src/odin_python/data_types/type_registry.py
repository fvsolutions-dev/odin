from typing import Dict
from pydantic import BaseModel
from typing import List, Any
from pydantic import Field
import csnake as cc
from abc import ABC, abstractmethod


class DataType(BaseModel, ABC):
    typename: str
    size: int = Field(description="Size of the data type in bytes")

    @abstractmethod
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable: ...

    @abstractmethod
    def to_c_array_initialiser(self, name: str, defaults: Any, dimensions: List[int]) -> cc.Variable: ...

    def extra_extension(self) -> str | None:
        return None


class StardardDataType(DataType):
    c_typename: str = Field(description="The C typename that corresponds to the data type")
    py_typename: str = Field(description="The python typename that corresponds to the data type")

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


class CustomDataType(StardardDataType):
    c_typename: str = Field(description="The C typename that corresponds to the data type")
    string_serialiser: str|None = Field(description="The string serialiser for the data type")
    default: Any | None = Field(description="The default value for the data type")

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
   
        if default is None:
            default = self.default
            
        assert default is not None, (
            "Default value must be provided, either in the parameter or in the type definition"
        )
        
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


class BooleanCDataType(StardardDataType):
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


class CharCDataType(StardardDataType):
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, "Default value must be provided"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(f"'{default}'"),  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any]|str|None, dimensions: List[int]) -> cc.Variable:

        if isinstance(defaults, str):
            value = cc.TextModifier(f'"{defaults}"')  # type: ignore
        elif defaults is None:
            value = [cc.TextModifier("0") ] # type: ignore
        else:
            value = [cc.TextModifier(f"'{x}'") for x in defaults]  # type: ignore
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=value,  # type: ignore
        )


BASE_DATA_TYPES: List[DataType] = [
    StardardDataType(typename="u64", size=8, c_typename="uint64_t", py_typename="OdinU64"),
    StardardDataType(typename="u32", size=4, c_typename="uint32_t", py_typename="OdinU32"),
    StardardDataType(typename="u16", size=2, c_typename="uint16_t", py_typename="OdinU16"),
    StardardDataType(typename="u8", size=1, c_typename="uint8_t", py_typename="OdinU8"),
    StardardDataType(typename="i64", size=8, c_typename="int64_t", py_typename="OdinI64"),
    StardardDataType(typename="i32", size=4, c_typename="int32_t", py_typename="OdinI32"),
    StardardDataType(typename="i16", size=2, c_typename="int16_t", py_typename="OdinI16"),
    StardardDataType(typename="i8", size=1, c_typename="int8_t", py_typename="OdinI8"),
    StardardDataType(typename="f32", size=4, c_typename="float", py_typename="OdinF32"),
    StardardDataType(typename="f64", size=8, c_typename="double", py_typename="OdinF64"),
    BooleanCDataType(typename="bool", size=1, c_typename="bool", py_typename="OdinBool"),
    CharCDataType(typename="char", size=1, c_typename="char", py_typename="OdinChar"),
]


class TypeRegistry:
    """The type registry, us used to store datatypes, it allows adding custom types"""

    def __init__(self):
        self.types: Dict[str, DataType] = {}

    def register(self, type: DataType | List[DataType]):
        """Register a new type"""

        if isinstance(type, list):
            for t in type:
                self.register(t)
            return

        if type.typename in self.types:
            raise ValueError(f"Type {type.typename} already registered")

        self.types[type.typename] = type

    def get_type(self, name: str):
        """Get a type by name"""

        if name not in self.types:
            raise ValueError(f"Type {name} not found")

        return self.types[name]
