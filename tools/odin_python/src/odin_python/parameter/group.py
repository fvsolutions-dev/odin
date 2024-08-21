from math import e
from typing import Dict

import csnake as cc
from pydantic import BaseModel, Field, PrivateAttr

from odin_python.parameter.access import (
    AccessConfigurationType,
    AccessConfigurations,
    AccessOptionsType,
    AccessOptionsTypeFactory,
)
from odin_python.utils.csnake_custom import StructVariable
from odin_python.utils.string import escape_string
from .parameter import LocalParameterModel, ParameterArrayModel, ReferenceParameterModel

from ..data_types.custom_structure import StructureDataType
from ..data_types.custom_enum import EnumeratorDataType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .store import ParameterStoreModel


class ParameterGroupModel(BaseModel):
    id: int
    _name: str = PrivateAttr()
    _parent: "ParameterGroupModel|ParameterStoreModel" = PrivateAttr()

    _access_configuration: AccessConfigurations = PrivateAttr()

    description: str | None = None
    children: "Dict[str, ParameterGroupModel| LocalParameterModel ]"

    access_permissions: AccessOptionsType = Field(
        default_factory=AccessOptionsTypeFactory
    )
    id_shift: int = 8

    @property
    def id_shift_bits(self) -> int:
        return self._parent.id_shift_bits - self.id_shift

    def calculate_id(self, id: int) -> int:
        return self._parent.calculate_id(self.id) + (id << self.id_shift_bits)
    
    @property
    def ram_location(self):
        return f"{self._parent.ram_location}.{self._name}"

    def init_children(
        self,
        parent: "ParameterGroupModel|ParameterStoreModel",
        name: str,
        access_permissions: AccessConfigurations | AccessConfigurationType,
    ):
        self._name = name
        self._parent = parent
        self._access_configuration = AccessConfigurations.inherit(
            access_permissions, self.access_permissions
        )

        for child_name, value in self.children.items():
            value.init_children(
                self,
                child_name,
                self._access_configuration,
            )

        return self

    def ram_struct(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> StructVariable:
        struct = StructVariable(var_name=self._name)
        for child in self.children.values():
            if isinstance(child, LocalParameterModel):
                struct.add_variable(child.to_c_initialiser(types))
            elif isinstance(child, ParameterGroupModel):
                struct.add_struct(child.ram_struct(types))
        return struct

    def to_c_odin_struct(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> StructVariable:
        struct = StructVariable(var_name=self._name)

        for child in self.children.values():
            if isinstance(child, LocalParameterModel):
                struct.add_variable(child.to_c_odin_parameter_initialiser(types))
            elif isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_c_odin_struct(types))

        return struct

    @property
    def c_type(self) -> str:
        assert self._name
        return f"{self._name}_t"
    
    # def to_c_tree(
    #     self, types: Dict[str, EnumeratorDataType | StructureDataType]
    # ) -> StructVariable:
        # struct = StructVariable(var_name=self._name)
        
        # for child_name, child in self.children.items():
        #     if isinstance(child, ParameterGroupModel):
        #         struct.add_struct(child.to_c_tree(types))
        #     else:
        #         struct.add_variable(child._name)
                
        
        # children = []
        # for child_name, child in self.children.items():
        #     if isinstance(child, ParameterGroupModel):
        #         children.append(child.to_c_tree(types).value)
        #     else:
        #         children.append(child._name)
                
        # return cc.Variable(
        #     name=f"{self._name}_tree",
        #     primitive="odin_tree_t",
        #     value={
        #         "name": self._name,
        #         "id": 0,
        #         "children": children,
        #     },
        # )
        
        
        
    # def to_c_typedef(
    #     self, types: Dict[str, EnumeratorDataType | StructureDataType]
    # ) -> cc.Struct:
    #     struct = cc.Struct(self.c_type, typedef=True)
    #     for parameter_name, parameter in self.children.items():
    #         if isinstance(parameter, ParameterGroupModel):
    #             struct.add_struct(parameter.to_c_typedef(types))
    #         if isinstance(parameter, LocalParameterModel):
    #             struct.add_variable(parameter.to_c_initialiser(types))
    #     return struct

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self._name,
            primitive=self.c_type,
            value={
                parameter_name: parameter.to_c_initialiser(types).value
                for parameter_name, parameter in self.children.items()  # type: ignore
            },
        )

    def to_c_odin_parameter_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self._name,
            primitive=self.c_type,
            value={
                parameter_name: parameter.to_c_odin_parameter_initialiser(types).value
                for parameter_name, parameter in self.children.items()  # type: ignore
            },
        )

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
    #         primitive="ODIN_parameter_group_t",
    #         value=data,
    #     )

    def to_c_odin_group(self, parameter_name: str) -> cc.Variable:
        params = []
        for name in self.children.keys():
            params.append(cc.TextModifier(f"&{parameter_name}.{self._name}.{name}"))

        return cc.Variable(
            name=self._name,
            primitive="ODIN_parameter_group_t",
            value={
                "name": self._name,
                "description": escape_string(self.description)
                if self.description
                else "No description",
                "index": cc.TextModifier(f"0x{self.id:08X}"),  # type: ignore
                "count": len(self.children),
                "parameters": params,
            },
        )
