from abc import ABC, abstractmethod
from ctypes import Union
from typing import Annotated, Any, Dict, List

import csnake as cc
from odin_python.parameter.access_control import AccessControlCollection
from odin_python.utils.csnake_custom import StructVariable
from odin_python.utils.string import escape_string
from pydantic import BaseModel, ConfigDict, Discriminator, Field, PrivateAttr, Tag

from ..data_types.type_registry import DataType, RegularCDataType, TypeRegistry
from ..extensions import Extensions
from .odin_defs import ODIN_ElementTypeEnum, ODIN_TypeEnum

ODIN_PARAMETER_TYPE = "ODIN_parameter_t"
MAX_ID_SIZE = 32


class ODIN_ParameterModel(BaseModel):
    access_group: str = Field(description="Access group")
    local_index: int = Field(description="Index of the parameter")
    global_index: int = Field(description="Global index of the parameter")

    data: str = Field(description="Reference to the data")
    type: DataType = Field(description="Resolved type of the parameter")
    name: str = Field(description="Name of the parameter")
    description: str = Field(description="Description of the parameter")
    extensions: None = Field(description="Extensions", default=None)

    @property
    def variable(self) -> cc.Variable:
        assert isinstance(self.type, RegularCDataType)

        return cc.Variable(
            name=self.name,
            primitive=ODIN_PARAMETER_TYPE,
            value={
                "odin_type": cc.TextModifier(
                    str(ODIN_TypeEnum.ODIN_TYPE_PARAMETER.value)
                ),
                "element_type": cc.TextModifier(
                    str(ODIN_ElementTypeEnum.from_c_type(self.type.c_typename).value)
                ),
                "flags": cc.TextModifier(str(self.access_group)),
                "global_index": cc.TextModifier(f"0x{self.global_index:08X}"),
                "element_size": cc.TextModifier(f"sizeof({self.type.c_typename})"),
                "data": cc.TextModifier(f"&{self.data}"),
                "name_and_description": rf"{self.name}\0{escape_string(self.description)}",
                "extension": cc.TextModifier(self.extensions)
                if self.extensions
                else cc.TextModifier("NULL"),
            },  # type: ignore
            comment=f"Local index: 0x{self.local_index:08X}",
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parameter.parameter import ParameterModel


class ODIN_ParameterGroupModel(BaseModel):
    param_name: str = Field(description="Name of the parameter group")
    name: str = Field(description="Name of the parameter group")
    description: str = Field(description="Description of the parameter group")
    global_id: int = Field(description="Global ID of the parameter group")
    id_space_shift: int = Field(description="ID space shift of the parameter group")
    # type: RegularCDataType = Field(description="Type of the parameter group")
    parameters_references: List[str] = Field(description="Parameters in the group")

    @property
    def variable(self) -> cc.Variable:
        parameters = []
        for parameter in self.parameters_references:

            parameters.append(
                cc.TextModifier(f"&{parameter}")
            )

        variable = cc.Variable(
            name=self.param_name,
            primitive="ODIN_parameter_group_t",
            value={  # type: ignore
                "name_and_description": rf"{self.name}\0{escape_string(self.description)}",
                "odin_type": cc.TextModifier(str(ODIN_TypeEnum.ODIN_TYPE_GROUP.value)),
                "global_index": cc.TextModifier(f"0x{self.global_id:08X}"),
                "shift": cc.TextModifier(str(self.id_space_shift)),
                "count": cc.TextModifier(str(len(parameters))),
                "parameters": parameters,
            },
        )
        return variable


class ODIN_ArrayModel(ODIN_ParameterModel):
    num_elements: int = Field(description="Number of elements in the array")
    fixed_size: bool = Field(description="Fixed size of the array", default=True)

    @property
    def variable(self) -> cc.Variable:
        variable = super().variable
        variable.value["odin_type"] = cc.TextModifier(  # type: ignore
            str(ODIN_TypeEnum.ODIN_TYPE_ARRAY.value)
            if self.fixed_size
            else str(ODIN_TypeEnum.ODIN_TYPE_VECTOR.value)
        )
        variable.value["max_elements"] = cc.TextModifier(str(self.num_elements))  # type: ignore
        return variable
