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
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        pass

    @abstractmethod
    def to_c_array_initialiser(
        self, name: str, default: Any, dimensions: List[int]
    ) -> cc.Variable:
        pass


class RegularCDataType(DataType):
    c_typename: str = Field(
        description="The C typename that corresponds to the data type"
    )

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(str(default)),  # type: ignore
        )

    def to_c_array_initialiser(
        self, name: str, default: List[Any] | None, dimensions: List[int]
    ) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=default if default else [0],  # type: ignore
        )


BASE_DATA_TYPES: List[DataType] = [
    RegularCDataType(typename="u64", size=8, c_typename="uint64_t"),
    RegularCDataType(typename="u32", size=4, c_typename="uint32_t"),
    RegularCDataType(typename="u16", size=2, c_typename="uint16_t"),
    RegularCDataType(typename="u8", size=1, c_typename="uint8_t"),
    RegularCDataType(typename="i64", size=8, c_typename="int64_t"),
    RegularCDataType(typename="i32", size=4, c_typename="int32_t"),
    RegularCDataType(typename="i16", size=2, c_typename="int16_t"),
    RegularCDataType(typename="i8", size=1, c_typename="int8_t"),
    RegularCDataType(typename="f32", size=4, c_typename="float"),
    RegularCDataType(typename="f64", size=8, c_typename="double"),
    RegularCDataType(typename="bool", size=1, c_typename="bool"),
    RegularCDataType(typename="char", size=1, c_typename="char"),
]


class TypeRegistry:
    def __init__(self):
        self.types: Dict[str, DataType] = {}

    def register(self, type: DataType | List[DataType]):
        """Register a new type"""

        if isinstance(type, list):
            for t in type:
                self.register(t)
            return

        if type.typename in self.types:
            raise ValueError(f"Type {type.__name__} already registered")

        self.types[type.typename] = type

    def get_type(self, name: str):
        """Get a type by name"""

        if name not in self.types:
            raise ValueError(f"Type {name} not found")

        return self.types[name]
