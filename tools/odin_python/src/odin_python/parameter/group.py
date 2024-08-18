from typing import Dict

import csnake as cc
from pydantic import BaseModel, Field, PrivateAttr

from odin_python.parameter.access import (
    AccessConfigurations,
    AccessOptionsType,
    AccessOptionsTypeFactory,
)
from .parameter import LocalParameterModel, ParameterArrayModel, ReferenceParameterModel

from ..data_types.custom_structure import StructureDataType
from ..data_types.custom_enum import EnumeratorDataType


class CNames(BaseModel):
    datastore_name: str = "ODIN_store"
    ram_params_name: str = "ODIN_ram"
    params_name: str = "ODIN_params"


class ParameterGroupModel(BaseModel):
    id: int
    _name: str = PrivateAttr()
    _parameter_location: str = PrivateAttr()
    # _variable_names: CNames | None = None
    _access_configuration: AccessConfigurations = PrivateAttr()

    description: str | None = None
    data: Dict[str, LocalParameterModel | ParameterArrayModel | ReferenceParameterModel]

    access_permissions: AccessOptionsType = Field(
        default_factory=AccessOptionsTypeFactory
    )

    def apply_naming(self):
        for k, v in self.data.items():
            v._name = k
            if isinstance(v, LocalParameterModel):
                v._parameter_location = f"{self._parameter_location}.{self._name}"
            v._group_name = self._name
            v._group_id = self.id
            v._access_configuration = AccessConfigurations.inherit(
                self._access_configuration, v.access_permissions
            )
        return self

    @property
    def c_type(self) -> str:
        assert self._name
        return f"{self._name}_t"

    def to_c_typedef(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Struct:
        struct = cc.Struct(self.c_type, typedef=True)
        for parameter_name, parameter in self.data.items():
            if isinstance(parameter, LocalParameterModel):
                struct.add_variable(parameter.to_c_initialiser(types))
        return struct

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self._name,
            primitive=self.c_type,
            value={
                parameter_name: parameter.to_c_initialiser(types).value
                for parameter_name, parameter in self.data.items()  # type: ignore
                if isinstance(parameter, LocalParameterModel)
            },
        )

    def to_c_odin_parameter_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return cc.Variable(
            name=self._name,
            primitive=self.c_type,
            value={
                parameter_name: parameter.to_c_odin_parameter(types).value
                for parameter_name, parameter in self.data.items()  # type: ignore
            },
        )
