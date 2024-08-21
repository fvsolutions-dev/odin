from typing import Any, Dict, Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from odin_python.parameter.access import (
    AccessConfigurationType,
    AccessConfigurations,
    AccessOptionsType,
    AccessOptionsTypeFactory,
)
from odin_python.utils.string import escape_string

# from .models import AccessOptionsGenerator, MainModel, DeviceGroupModel

from ..data_types.custom_enum import EnumeratorDataType
from ..data_types.custom_structure import GenericDataType, StructureDataType
from ..data_types.standard_types import CFormatEnum, StandardCTypesEnum
import csnake as cc
from ..extensions import (
    EXENSIONS,
    MappingParameterExtensionModel,
)

ODIN_PARAMETER_TYPE = "ODIN_parameter_t"

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .store import ParameterStoreModel
    from .group import ParameterGroupModel


class BaseParameterModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    _name: str = PrivateAttr()
    _parent: "ParameterGroupModel|ParameterStoreModel" = PrivateAttr()
    _access_configuration: AccessConfigurations = PrivateAttr()

    id: int
    primitive: StandardCTypesEnum | str = Field(union_mode="left_to_right")
    description: str | None = None
    access_permissions: AccessOptionsType = Field(
        default_factory=AccessOptionsTypeFactory
    )

    format: CFormatEnum = Field(
        default=CFormatEnum.AUTO,
        description="The format of the data. If set to 'auto', the format will be determined based on the primitive type.",
    )

    def primitive_type(self, types) -> StandardCTypesEnum | GenericDataType:
        if isinstance(self.primitive, StandardCTypesEnum):
            return self.primitive
        return types[self.primitive]

    @property
    def qualified_id(self) -> int:
        return self._parent.calculate_id(self.id)

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


class LocalParameterModel(BaseParameterModel):
    """Stores all the information for a parameter."""

    default: Any | None = None
    extension: EXENSIONS | None = None

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return self.primitive_type(types).to_c_initialiser(
            types, self._name, self.default
        )

    @property
    def ram_location(self):
        return f"{self._parent.ram_location}.{self._name}"

    def to_c_odin_parameter_initialiser(
        self, types, name_prefix: str | None = None
    ) -> cc.Variable:
        primitive_type = self.primitive_type(types)

        permission_flags = self._access_configuration.get_permission_flags()

        return cc.Variable(
            name=f"{name_prefix}{self._name}" if name_prefix else self._name,
            primitive=ODIN_PARAMETER_TYPE,
            value={
                "index": cc.TextModifier(f"0x{self.qualified_id:08X}"),
                "access": cc.TextModifier(
                    "|".join(permission_flags) if permission_flags else "0"
                ),
                "format": cc.TextModifier(
                    primitive_type.default_format.odin_type_macro
                    if self.format == CFormatEnum.AUTO
                    else self.format.odin_type_macro
                ),
                "type": cc.TextModifier(primitive_type.element_type.odin_type_macro),
                "data": cc.TextModifier(f"&{self.ram_location}"),
                "size": cc.TextModifier(f"sizeof({self.ram_location})"),
                "name": self._name,
                "description": escape_string(self.description)
                if self.description
                else "No description",
            },  # type: ignore
        )

        # if self.extension:
        #     data["extension"] = self.extension.as_literal()

        # if self._is_reference:
        #     data["data"] = FormattedLiteral("NULL", string_formatter=str)

        # return data


class ParameterArrayModel(LocalParameterModel):
    length: int

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ):
        return self.primitive_type(types).to_c_array_initaliser(
            types, self._name, self.default, self.length
        )


class ParameterNullTerminatedArrayModel(ParameterArrayModel):
    null_terminated: Literal[True] = True


class ReferenceParameterModel(BaseParameterModel):
    referenced_parameter: str

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> None:
        return None

    def to_c_odin_parameter(self, types, name_prefix: str | None = None) -> cc.Variable:
        primitive_type = self.primitive_type(types)

        permission_flags = self._access_configuration.get_permission_flags()

        return cc.Variable(
            name=f"{name_prefix}{self._name}" if name_prefix else self._name,
            primitive=ODIN_PARAMETER_TYPE,
            value={
                "index": cc.TextModifier(f"0x{self.qualified_id:08X}"),
                "access": cc.TextModifier(
                    "|".join(permission_flags) if permission_flags else "0"
                ),
                "format": cc.TextModifier(
                    primitive_type.default_format.odin_type_macro
                    if self.format == CFormatEnum.AUTO
                    else self.format.odin_type_macro
                ),
                "type": cc.TextModifier(primitive_type.element_type.odin_type_macro),
                "data": cc.TextModifier(f"&{self.referenced_parameter}"),
                "size": cc.TextModifier(f"sizeof({self.referenced_parameter})"),
                "name": self._name,
                "description": escape_string(self.description)
                if self.description
                else "No description",
            },  # type: ignore
        )
