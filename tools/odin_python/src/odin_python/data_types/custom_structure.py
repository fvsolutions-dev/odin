from typing import Any, Dict, List, Literal

import csnake as cc
from pydantic import BaseModel, Field, PrivateAttr, model_validator


from .__generic__ import GenericDataType
from .standard_types import CustomCTypesEnum, StandardCTypesEnum, CFormatEnum
from .custom_enum import EnumeratorDataType


class StructureDataType(GenericDataType):
    class Member(BaseModel):
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

        def to_type(self, types):
            if isinstance(self.primitive, StandardCTypesEnum):
                return self.primitive

            elif self.primitive in types:
                return types[self.primitive]

            raise ValueError(f"Type {self.primitive} not found in {types.keys()}")

    type: Literal["structured"]

    structure: Dict[str, Member]

    def to_c_typedef(self) -> cc.Struct:
        var = cc.Struct(
            name=self._typename,
            typedef=True,
        )

        for k, v in self.structure.items():
            var.add_variable(
                v.to_variable(),
            )

        return var

    def to_c_value(
        self,
        types: "Dict[str, StructureDataType|EnumeratorDataType]",
        value: Dict[str, Any] | None,
    ) -> Dict[str, cc.TextModifier]:
        fields = {}
        for k, v in self.structure.items():
            type = v.to_type(types)
            if value is None:
                fields[k] = type.to_c_value(types, v.default)
            elif k in value:
                fields[k] = type.to_c_value(types, value[k])
            else:
                fields[k] = type.to_c_value(types, v.default)
        return fields

    def to_c_array_initaliser(
        self,
        types: "Dict[str, StructureDataType|EnumeratorDataType]",
        name: str,
        default_item: List[Dict[str, Any]] | None,
        lenght: int,
    ) -> cc.Variable:
        if default_item is not None:
            assert len(default_item) == lenght, f"Length of {name} is not {lenght}"

        values = []
        for i in range(lenght):
            fields = {}

            if default_item is not None:
                default = default_item[i]
            else:
                default = None

            for k, v in self.structure.items():
                type = v.to_type(types)
                if default is None:
                    value = type.to_c_value(types, v.default)
                elif k in default:
                    value = type.to_c_value(types, default[k])
                else:
                    value = type.to_c_value(types, v.default)

                fields[k] = value
            values.append(fields)

        ret = cc.Variable(
            name=name,
            primitive=self._typename,
            value=values,  # type: ignore
            array=[lenght],
        )
        return ret

    def to_c_initialiser(
        self,
        types: "Dict[str, StructureDataType|EnumeratorDataType]",
        name: str,
        default: Dict[str, Any] | None,
    ) -> cc.Variable:
        fields = {}
        for k, v in self.structure.items():
            type = v.to_type(types)
            if default is None:
                value = type.to_c_value(types, v.default)
            elif k in default:
                value = type.to_c_value(types, default[k])
            else:
                value = type.to_c_value(types, v.default)

            fields[k] = value

        ret = cc.Variable(
            name=name,
            primitive=self._typename,
            value=fields,  # type: ignore
        )
        return ret

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.structure.items():
            v._name = k
        return self

    @property
    def default_format(self) -> CFormatEnum:
        return CFormatEnum.HEX

    @property
    def element_type(self) -> CustomCTypesEnum:
        return CustomCTypesEnum.STRUCTURED
