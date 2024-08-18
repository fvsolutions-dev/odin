from typing import Dict

import csnake as cc
from pydantic import BaseModel

from odin_python.utils.csnake_custom import StructVariable

from ..data_types.custom_enum import EnumeratorDataType
from ..data_types.custom_structure import StructureDataType
from .group import ParameterGroupModel




class ParameterStoreModel(BaseModel):
    name: str
    groups: Dict[str, ParameterGroupModel]

    @property
    def c_type(self) -> str:
        return f"{self.name}_t"

    def to_recursive_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = StructVariable(self.c_type, typedef=True)

        # Create the data structures for groups
        for group_name, device_group in self.groups.items():
            group_struct = StructVariable(var_name=group_name)

            for parameter in device_group.data.values():
                group_struct.add_variable(parameter.to_c_initialiser(types))

            struct.add_struct(group_struct)

        return struct

    def to_c_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = cc.Struct(self.c_type, typedef=True)

        for group in self.groups.values():
            struct.add_variable(group.to_c_initialiser(types))

        return struct

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self.name,
            primitive=self.c_type,
            value={
                group_name: group.to_c_initialiser(types).value
                for group_name, group in self.groups.items()  # type: ignore
            },
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
