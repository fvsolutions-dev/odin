from typing import Dict
from pydantic import BaseModel
from typing import List
from pydantic import Field


class DataType(BaseModel):
    typename: str
    size: int = Field(description="Size of the data type in bytes")
    c_typename: str = Field(
        description="The C typename that corresponds to the data type"
    )


BASE_DATA_TYPES = [
    DataType(typename="u64", size=8, c_typename="uint64_t"),
    DataType(typename="u32", size=4, c_typename="uint32_t"),
    DataType(typename="u16", size=2, c_typename="uint16_t"),
    DataType(typename="u8", size=1, c_typename="uint8_t"),
    DataType(typename="i64", size=8, c_typename="int64_t"),
    DataType(typename="i32", size=4, c_typename="int32_t"),
    DataType(typename="i16", size=2, c_typename="int16_t"),
    DataType(typename="i8", size=1, c_typename="int8_t"),
    DataType(typename="f32", size=4, c_typename="float"),
    DataType(typename="f64", size=8, c_typename="double"),
    DataType(typename="bool", size=1, c_typename="bool"),
    DataType(typename="char", size=1, c_typename="char"),
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
