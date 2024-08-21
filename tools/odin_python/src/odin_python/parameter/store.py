from math import e
import re
from typing import Dict

import csnake as cc
from pydantic import BaseModel

from odin_python.parameter.access import (
    AccessConfigurationType,
    AccessOptionsType,
    AccessOptionsTypeFactory,
)
from odin_python.parameter.parameter import LocalParameterModel
from odin_python.utils.csnake_custom import StructVariable

from ..data_types.custom_enum import EnumeratorDataType
from ..data_types.custom_structure import StructureDataType
from .group import ParameterGroupModel
from pydantic import PrivateAttr, Field, model_validator


class ParameterStoreModel(BaseModel):
    ram_name: str
    parameter_name: str

    children: Dict[str, ParameterGroupModel | LocalParameterModel]
    access_permissions: AccessConfigurationType
    id_size: int = 32
    id_shift: int = 8

    @model_validator(mode="after")
    def init_children(self):
        for name, item in self.children.items():
            item.init_children(self, name, self.access_permissions)
        return self

    @property
    def id_shift_bits(self) -> int:
        return self.id_size - self.id_shift

    def calculate_id(self, id: int) -> int:
        return id << self.id_shift_bits

    @property
    def ram_location(self):
        return self.ram_name

    @property
    def c_type(self) -> str:
        return f"{self.ram_name}_t"

    @property
    def odin_c_type(self) -> str:
        return f"{self.parameter_name}_t"

    def ram_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = StructVariable(self.c_type, typedef=True)

        # Create the data structures for groups
        for child in self.children.values():
            if isinstance(child, LocalParameterModel):
                struct.add_variable(child.to_c_initialiser(types))
            elif isinstance(child, ParameterGroupModel):
                struct.add_struct(child.ram_struct(types))

        return struct

    def to_recursive_odin_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = StructVariable(self.odin_c_type, typedef=True)

        # Create the data structures for groups
        for child in self.children.values():
            if isinstance(child, LocalParameterModel):
                struct.add_variable(child.to_c_odin_parameter_initialiser(types))
            elif isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_c_odin_struct(types))

        return struct

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        values = {}
        for child_name, child in self.children.items():
            values[child_name] = child.to_c_initialiser(types).value

        return cc.Variable(
            name=self.ram_name,
            primitive=self.c_type,
            value=values,  # type: ignore
        )

    def to_c_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = cc.Struct(self.c_type, typedef=True)

        for group in self.children.values():
            struct.add_variable(group.to_c_initialiser(types))

        return struct

    def to_c_odin_parameter_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self.parameter_name,
            primitive=self.odin_c_type,
            value={
                group_name: group.to_c_odin_parameter_initialiser(types).value
                for group_name, group in self.children.items()  # type: ignore
            },
        )

    def to_tree_definition(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        children = []
        for child_name, child in self.children.items():
            if isinstance(child, LocalParameterModel):
                children.append(child._name)

            elif isinstance(child, ParameterGroupModel):
                children.append(child.to_c_tree(types))

        return cc.Variable(
            name=f"{self.parameter_name}_tree",
            primitive="odin_tree_t",
            value={
                "name": self.parameter_name,
                "id": 0,
                "children": children,
            },  # type: ignore
        )

    # def as_variable_initialization(self) -> cc.Variable:
    #     assert self._name

    #     return cc.Variable(
    #         name=self._name,
    #         primitive=self.c_type,
    #         value={
    #             parameter_name: parameter.default
    #             for parameter_name, parameter in self.data.items()
    #         },
    #     )

    # def as_parameter_group(self, acces_opt: "AccessOptionsGenerator") -> Dict:
    #     params = {}
    #     for parameter_name, parameter in self.data.items():
    #         params[parameter_name] = parameter.as_parameter(acces_opt)
    #     return params

    # def as_reference(self) -> cc.Variable:
    #     params = []
    #     for parameter_name, parameter in self.data.items():
    #         params.append(
    #             FormattedLiteral(
    #                 f"&{parameter.parameter_reference}", string_formatter=str
    #             )
    #         )

    #     data = {
    #         "name": self._name,
    #         "description": escape_string(self.description),
    #         "index": FormattedLiteral(self.id, int_formatter=hex),
    #         "count": len(self.data),
    #         "parameters": params,
    #     }

    #     return cc.Variable(
    #         name=self.group_reference,
    #         primitive=ODIN_GROUP_TYPE,
    #         value=data,
    #     )
