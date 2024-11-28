from typing import Dict
from pydantic import BaseModel
from typing import List
from pydantic import Field


class DataType(BaseModel):
    typename: str
    size: int = Field(description="Size of the data type in bytes")


BASE_DATA_TYPES = [
    DataType(typename="u32", size=4),
    DataType(typename="u16", size=2),
    DataType(typename="u8", size=1),
    DataType(typename="i32", size=4),
    DataType(typename="i16", size=2),
    DataType(typename="i8", size=1),
    DataType(typename="f32", size=4),
    DataType(typename="f64", size=8),
    DataType(typename="bool", size=1),
    DataType(typename="char", size=1),
]


class TypeRegistry:
    def __init__(self):
        self._types: Dict[str, DataType] = {}

    def register(self, type: DataType | List[DataType]):
        """Register a new type"""

        if isinstance(type, list):
            for t in type:
                self.register(t)
            return

        if type.__name__ in self._types:
            raise ValueError(f"Type {type.__name__} already registered")

        if not issubclass(type, DataType):
            raise ValueError(f"Type {type.__name__} is not a subclass of BaseType")

        self._types[type.__name__] = type

    def get_type(self, name: str):
        """Get a type by name"""

        if name not in self._types:
            raise ValueError(f"Type {name} not found")

        return self._types[name]
