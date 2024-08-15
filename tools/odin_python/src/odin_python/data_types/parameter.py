import csnake as cc

# from .models import AccessOptionsGenerator, MainModel, DeviceGroupModel
from pydantic_yaml import parse_yaml_file_as
from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from .types import StandardCTypesEnum
from typing import Any, Dict
from .data_types import StructDataType, EnumDataType

class ParameterModel(BaseModel):
    """Stores all the information for a parameter."""

    _name: str = PrivateAttr()
    _group_name: str = PrivateAttr()
    _group_id: int = PrivateAttr()
    _types: Dict[str, StructDataType | EnumDataType] = PrivateAttr()
    
    id: int
    primitive: StandardCTypesEnum | str = Field(union_mode="left_to_right")

    default: Any
    description: str = ""

    def to_c_object(self):
        if isinstance(self.primitive, StandardCTypesEnum):
            return cc.Variable(
                name=self._name,
                primitive=self.primitive.value,
                value=self.default,
            )
        else:
            
            type = self._types[self.primitive]
            
            model = type.to_model(self._types)
            print(model, self.primitive)
             
            # Initialize the model with the default value
            
            # print(value.to_string())
            return cc.Variable(
                name=self._name,
                primitive=self.primitive,
                value=model.as_reference(self.default),
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
