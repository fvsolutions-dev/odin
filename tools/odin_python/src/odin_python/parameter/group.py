from typing import Dict

import csnake as cc
from pydantic import BaseModel, model_validator, PrivateAttr

# from .extensions import (
#     EXENSIONS,
#     ReferenceParameterExtensionModel,
# )
# from .types import CFormatEnum, CTypeEnum
# from .utils.csnake_custom import StructVariable
# from .utils.string import escape_string
from .parameter import ParameterModel, ParameterArrayModel

from ..data_types.custom_structure import StructureDataType
from ..data_types.custom_enum import EnumeratorDataType


class CNames(BaseModel):
    datastore_name: str = "ODIN_store"
    ram_params_name: str = "ODIN_ram"
    params_name: str = "ODIN_params"


class ParameterGroupModel(BaseModel):
    id: int
    _name: str = PrivateAttr()
    # _variable_names: CNames | None = None

    description: str
    data: Dict[str, ParameterModel | ParameterArrayModel]
    # access_permissions: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.data.items():
            v._name = k

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
            },
        )
