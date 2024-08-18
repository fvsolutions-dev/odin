from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from odin_python.parameter.access import (
    AccessConfigurations,
    AccessOptionsType,
    AccessOptionsTypeFactory,
)
from odin_python.utils.string import escape_string

# from .models import AccessOptionsGenerator, MainModel, DeviceGroupModel

from ..data_types.custom_enum import EnumeratorDataType
from ..data_types.custom_structure import GenericDataType, StructureDataType
from ..data_types.standard_types import StandardCTypesEnum
import csnake as cc

ODIN_PARAMETER_TYPE = "ODIN_parameter_t"


class ParameterModel(BaseModel):
    """Stores all the information for a parameter."""

    model_config = ConfigDict(extra="forbid")

    _name: str = PrivateAttr()
    _group_name: str | None = PrivateAttr()
    _group_id: int | None = PrivateAttr()
    _parameter_location: str | None = PrivateAttr()
    _access_configuration: AccessConfigurations = PrivateAttr()

    id: int
    primitive: StandardCTypesEnum | str = Field(union_mode="left_to_right")

    access_permissions: AccessOptionsType = Field(
        default_factory=AccessOptionsTypeFactory
    )

    default: Any | None = None
    description: str | None = None

    def primitive_type(self, types) -> StandardCTypesEnum | GenericDataType:
        if isinstance(self.primitive, StandardCTypesEnum):
            return self.primitive
        return types[self.primitive]

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ) -> cc.Variable:
        return self.primitive_type(types).to_c_initialiser(
            types, self._name, self.default
        )

    @property
    def qualified_id(self) -> int:
        return (
            (self._group_id << 16) | self.id if self._group_id is not None else self.id
        )

    def to_c_odin_parameter(self, types, name_prefix: str | None = None) -> cc.Variable:
        primitive_type = self.primitive_type(types)

        paramter_location = (
            f"{self._parameter_location}.{self._name}"
            if self._parameter_location
            else self._name
        )
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
                ),
                "type": cc.TextModifier(primitive_type.element_type.odin_type_macro),
                "data": cc.TextModifier(f"&{paramter_location}"),
                "size": cc.TextModifier(f"sizeof({paramter_location})"),
                "name": self._name,
                "description": escape_string(self.description)
                if self.description
                else "No description",
            },  # type: ignore
        )

        # data = {
        #     "index": FormattedLiteral(id, int_formatter=hex),
        #     "access": access_opts.as_literal(self),
        #     "format": FormattedLiteral(
        #         self.format.odin_type_conv(self.primitive, self.length),
        #         string_formatter=str,
        #     ),
        #     "type": FormattedLiteral(
        #         self.primitive.odin_type_macro, string_formatter=str
        #     ),
        #     "data": FormattedLiteral(
        #         f"&{self.variable_reference}", string_formatter=str
        #     ),
        #     "size": FormattedLiteral(
        #         self.primitive.sizeof(self.length), string_formatter=str
        #     ),
        #     "name": self._name,
        #     "description": escape_string(self.description),
        # }

        # if self.extension:
        #     data["extension"] = self.extension.as_literal()

        # if self._is_reference:
        #     data["data"] = FormattedLiteral("NULL", string_formatter=str)

        # return data


class ParameterArrayModel(ParameterModel):
    length: int

    def to_c_initialiser(
        self, types: Dict[str, EnumeratorDataType | StructureDataType]
    ):
        return self.primitive_type(types).to_c_array_initaliser(
            types, self._name, self.default, self.length
        )

    # _variable_names: CNames | None = None

    # _ram_params_name: str | None = None
    # _variable_store_name: str | None = None
    # _is_reference: bool = False

    # id: int

    # access_permissions: Dict[str, str] = Field(default_factory=dict)
    # format: CFormatEnum = Field(
    #     default=CFormatEnum.AUTO,
    #     description="The format of the data. If set to 'auto', the format will be determined based on the primitive type.",
    # )
    # length: int | None = None

    # persistent: bool = False
    # extension: EXENSIONS | None = None

    # @model_validator(mode="after")
    # def check_reference(self) -> "ParameterModel":
    #     if self.extension and isinstance(
    #         self.extension, ReferenceParameterExtensionModel
    #     ):
    #         self._is_reference = True
    #     return self

    # @property
    # def qualified_id(self) -> int:
    #     assert self._group_id is not None
    #     return (self._group_id << 16) | self.id

    # @property
    # def variable_reference(self):
    #     assert self._variable_names
    #     assert self._name
    #     assert self._group_name
    #     return f"{self._variable_names.ram_params_name}.{self._group_name}.{self._name}"

    # @property
    # def parameter_reference(self):
    #     assert self._name
    #     assert self._group_name
    #     assert self._variable_names
    #     return f"{self._variable_names.params_name}.{self._group_name}.{self._name}"

    # def as_variable(self) -> cc.Variable:
    #     assert self._name
    #     return cc.Variable(
    #         name=self._name,
    #         primitive=self.primitive,
    #         array=[self.length] if self.length else None,
    #     )

    # def as_parameter(self, access_opts: "AccessOptionsGenerator") -> Dict:
    #     assert self._group_id is not None
    #     id = (self._group_id << 16) | self.id
    #     data = {
    #         "index": FormattedLiteral(id, int_formatter=hex),
    #         "access": access_opts.as_literal(self),
    #         "format": FormattedLiteral(
    #             self.format.odin_type_conv(self.primitive, self.length),
    #             string_formatter=str,
    #         ),
    #         "type": FormattedLiteral(
    #             self.primitive.odin_type_define, string_formatter=str
    #         ),
    #         "data": FormattedLiteral(
    #             f"&{self.variable_reference}", string_formatter=str
    #         ),
    #         "size": FormattedLiteral(
    #             self.primitive.sizeof(self.length), string_formatter=str
    #         ),
    #         "name": self._name,
    #         "description": escape_string(self.description),
    #     }

    #     if self.extension:
    #         data["extension"] = self.extension.as_literal()

    #     if self._is_reference:
    #         data["data"] = FormattedLiteral("NULL", string_formatter=str)

    #     return data

    # def as_odin_parameter(self) -> cc.Variable:
    #     var = cc.Variable(
    #         name=self._name,
    #         primitive=ODIN_PARAMETER_TYPE,
    #     )
    #     return var

    # def as_ram_parameter(self) -> cc.Variable | None:
    #     if self._is_reference:
    #         return None

    #     var = cc.Variable(
    #         name=self._name,
    #         primitive=self.primitive,
    #         array=[self.length] if self.length else None,
    #         value=self.default,
    #     )
    #     return var

    # def to_values(self, data: bytes):
    #     if self.length is not None:
    #         return data

    #     if self.primitive == StandardCTypesEnum.UINT8:
    #         return struct.unpack("B", data)[0]
    #     if self.primitive == StandardCTypesEnum.INT8:
    #         return struct.unpack("b", data)[0]
    #     if self.primitive == StandardCTypesEnum.UINT16:
    #         return struct.unpack("H", data)[0]
    #     if self.primitive == StandardCTypesEnum.INT16:
    #         return struct.unpack("h", data)[0]
    #     if self.primitive == StandardCTypesEnum.UINT32:
    #         return struct.unpack("I", data)[0]
    #     if self.primitive == StandardCTypesEnum.INT32:
    #         return struct.unpack("i", data)[0]
    #     if self.primitive == StandardCTypesEnum.UINT64:
    #         return struct.unpack("Q", data)[0]
    #     if self.primitive == StandardCTypesEnum.INT64:
    #         return struct.unpack("q", data)[0]
    #     if self.primitive == StandardCTypesEnum.FLOAT:
    #         return struct.unpack("f", data)[0]
    #     if self.primitive == StandardCTypesEnum.DOUBLE:
    #         return struct.unpack("d", data)[0]
    #     if self.primitive == StandardCTypesEnum.BOOL:
    #         return bool(data[0])
