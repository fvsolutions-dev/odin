from typing import Dict, Literal

import csnake as cc
from pydantic import BaseModel, PrivateAttr, model_validator
from typing import Any
import enum
from typing import Type
from pydantic import create_model, BaseModel, Field, PrivateAttr
from .types import StandardCTypesEnum
from abc import ABC, abstractmethod


class DataTypeABC(BaseModel, ABC):
    """Base class for all data types

    A type represents a data type that can be used in the system.
    """

    _typename: str = PrivateAttr()  # Name of the type

    @abstractmethod
    def initialise_model(self, value: Any): ...

    @property
    @abstractmethod
    def model(self): ...


class StructureMembers(BaseModel):
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


class Structure(DataTypeABC):
    type: Literal["structured"]
    structure: Dict[str, StructureMembers]

    _model: Type[BaseModel] | None = PrivateAttr(default=None)
    _types: "Dict[str, Structure | Enumerator]" = PrivateAttr()

    @property
    def model(self):
        if self._model is not None:
            return self._model

        fields = {}
        for k, v in self.structure.items():
            if isinstance(v.primitive, StandardCTypesEnum):
                local_primitive = v.primitive
            else:
                local_primitive = self._types[v.primitive]

            type = local_primitive.model
            value = local_primitive.initialise_model(v.default)
            fields[k] = (type, value)

        self._model = create_model(f"{self._typename}Model", **fields)
        return self._model

    def initialise_model(self, value: Any):
        return self.model(**value)

    # def to_c_object(self):
    #     var = cc.Struct(
    #         name=f"{self._typename}_t",
    #         typedef=True,
    #     )

    #     for k, v in self.structure.items():
    #         var.add_variable(
    #             v.to_variable(),
    #         )

    #     return var

    # @model_validator(mode="after")
    # def populate_names(self):
    #     for k, v in self.structure.items():
    #         v._name = k
    #     return self

    # def as_type(self, types):
    #     # Create pydantic model

    #     # d = {f"{self._name}Model": {"name": "test_strat2", "periods": 10}}
    #     fields = {}
    #     for k, v in self.structure.items():
    #         if isinstance(v.primitive, StandardCTypesEnum):
    #             type = v.primitive.to_type()
    #             fields[k] = (type, type(v.default))
    #         else:
    #             type = types[v.primitive].to_model(types)
    #             fields[k] = (type._enum, type.enum_value_from_value(v.default))

    #     Strategy = create_model(f"{self._typename}Model", **fields)
    #     return Strategy


class Enumerator(DataTypeABC):
    type: Literal["enumerator"]
    values: Dict[str, int]

    _model: enum.Enum | None = PrivateAttr(default=None)

    @property
    def model(self) -> enum.Enum:
        if self._model is not None:
            return self._model

        values = {k.upper(): v for k, v in self.values.items()}
        self._model = enum.Enum(self._typename, values)
        return self._model

    def initialise_model(self, value: str | int):
        """Returns the specified value for the enum.
        Match by name or by value
        """

        for k, v in self.values.items():
            if k == value or v == value:
                return self.model(v)  # type: ignore
        raise ValueError(f"Value {value} not found in {self._typename}")

    # @property
    # def prefix(self):
    #     return f"{self._typename.upper()}_"

    # @property
    # def c_type_name(self):
    #     return f"{self._typename}_t"

    # def to_c_object(self):
    #     enum = cc.Enum(
    #         name=self.c_type_name,
    #         typedef=True,
    #         prefix=self.prefix,
    #     )

    #     for k, v in self.values.items():
    #         enum.add_value(name=k.upper(), value=v)  # type: ignore

    #     return enum

    # def as_type(self, to_model):
    #     object = self.to_c_object()
    #     return EnumDataty(object.name, self.prefix, {v.name: v for v in object.values})


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
