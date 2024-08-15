from typing import Dict, Literal

import csnake as cc
from pydantic import BaseModel, PrivateAttr, model_validator
from typing import Any
import enum
from typing import Type
from pydantic import create_model, BaseModel, Field, PrivateAttr
from .types import StandardCTypesEnum


class StructureContent(BaseModel):
    _name: str = PrivateAttr()
    primitive: StandardCTypesEnum | str = Field(union_mode="left_to_right")
    length_bits: int | None = None
    description: str = "    "
    default: Any | None = None

    def to_variable(self):
        if self.length_bits is None:
            name = self._name
        else:
            name = f"{self._name}:{self.length_bits}"

        return cc.Variable(
            name=name,
            primitive=self.primitive,
        )


class StructDataType(BaseModel):
    type: Literal["structured"]
    _name: str = PrivateAttr()
    structure: Dict[str, StructureContent]

    def to_c_object(self):
        var = cc.Struct(
            name=f"{self._name}_t",
            typedef=True,
        )

        for k, v in self.structure.items():
            var.add_variable(
                v.to_variable(),
            )

        return var

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.structure.items():
            v._name = k
        return self

    def to_model(self, types):
        # Create pydantic model

        # d = {f"{self._name}Model": {"name": "test_strat2", "periods": 10}}
        fields = {}
        for k, v in self.structure.items():
            if isinstance(v.primitive, StandardCTypesEnum):
                type = v.primitive.to_type()
                fields[k] = (type, type(v.default))
            else:
                type = types[v.primitive].to_model(types)
                fields[k] = (type._enum, type.enum_value_from_value(v.default))

        Strategy = create_model(f"{self._name}Model", **fields)
        return Strategy


class EnumDataty:
    def __init__(self, name, prefix, values):
        self.name = name
        self.values = values
        self.prefix = prefix

        self._enum = enum.Enum(name, values)

    def enum_value_from_value(self, value) -> enum.Enum:
        # Get by name or by value
        for k, v in self.values.items():
            if k == value or v == value:
                return v
        raise ValueError(f"Value {value} not found in {self.name}")
    

    def from_value(self, key) -> cc.Enum.EnumValue:
        # Match by key
        for k, v in self.values.items():
            if k == key:
                return v
        raise ValueError(f"Key {key} not found in {self.name}")

    def get_tpedef(self, enum: cc.Enum.EnumValue):
        return f"{self.name}"

    def as_reference(self, key):
        value = self.from_value(key)
        return cc.TextModifier(f"{self.prefix.upper()}{value.name.upper()}")


class EnumDataType(BaseModel):
    type: Literal["enumerator"]
    _name: str = PrivateAttr()
    values: Dict[str, int]

    @property
    def prefix(self):
        return f"{self._name.upper()}_"

    def to_c_object(self):
        var = cc.Enum(
            name=f"{self._name}_t",
            typedef=True,
            prefix=self.prefix,
        )

        for k, v in self.values.items():
            var.add_value(name=k.upper(), value=v)  # type: ignore

        return var

    def to_model(self, to_model):
        object = self.to_c_object()
        return EnumDataty(object.name, self.prefix, {v.name: v for v in object.values})
