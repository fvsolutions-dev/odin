from typing import Union

import csnake as cc
from strenum import StrEnum
from typing import Any

import struct


class CTypesEnum(StrEnum):
    @property
    def odin_type_macro(self) -> str:
        return f"ODIN_ELEMENT_TYPE_{self.name}"


class CustomCTypesEnum(CTypesEnum):
    ENUMERATOR = "enumerator"
    STRUCTURED = "structured"


class StandardCTypesEnum(CTypesEnum):
    UINT8 = "uint8_t"
    INT8 = "int8_t"
    INT16 = "int16_t"
    UINT16 = "uint16_t"
    INT32 = "int32_t"
    UINT32 = "uint32_t"
    UINT64 = "uint64_t"
    INT64 = "int64_t"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    BOOL = "bool"

    def sizeof(self, length: int | None) -> str:
        if length is None:
            return f"sizeof({self.value})"
        else:
            return f"sizeof({self.value})*{length}"

    def to_c_initialiser(self, types, name: str, default: Any) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.value,
            value=self.to_c_value(types, default),  # type: ignore
        )

    def to_c_array_initaliser(
        self, types, name: str, default: Any, length: int
    ) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.value,
            value=default,
            array=[length],
        )

    def to_c_value(self, types, value: Any) -> cc.TextModifier:
        return cc.TextModifier(str(value))

    def to_python_primitive(self, data: bytes) -> Union[int, float, str, bool]:
        if self in [StandardCTypesEnum.UINT8, StandardCTypesEnum.INT8]:
            return struct.unpack("b", data)[0]
        if self in [StandardCTypesEnum.UINT16, StandardCTypesEnum.INT16]:
            return struct.unpack("h", data)[0]
        if self in [StandardCTypesEnum.UINT32, StandardCTypesEnum.INT32]:
            return struct.unpack("i", data)[0]
        if self in [StandardCTypesEnum.UINT64, StandardCTypesEnum.INT64]:
            return struct.unpack("q", data)[0]
        if self == StandardCTypesEnum.FLOAT:
            return struct.unpack("f", data)[0]
        if self == StandardCTypesEnum.DOUBLE:
            return struct.unpack("d", data)[0]
        if self == StandardCTypesEnum.CHAR:
            return struct.unpack("c", data)[0]
        if self == StandardCTypesEnum.BOOL:
            return struct.unpack("?", data)[0]

        raise ValueError(f"Unsupported primitive type {self}")

    def to_c_primitive(self, data: Union[int, float, str, bool]) -> bytes:
        if self in [StandardCTypesEnum.UINT8, StandardCTypesEnum.INT8]:
            return struct.pack("b", data)
        if self in [StandardCTypesEnum.UINT16, StandardCTypesEnum.INT16]:
            return struct.pack("h", data)
        if self in [StandardCTypesEnum.UINT32, StandardCTypesEnum.INT32]:
            return struct.pack("i", data)
        if self in [StandardCTypesEnum.UINT64, StandardCTypesEnum.INT64]:
            return struct.pack("q", data)
        if self == StandardCTypesEnum.FLOAT:
            return struct.pack("f", data)
        if self == StandardCTypesEnum.DOUBLE:
            return struct.pack("d", data)
        if self == StandardCTypesEnum.CHAR:
            return struct.pack("c", data)
        if self == StandardCTypesEnum.BOOL:
            return struct.pack("?", data)

        raise ValueError(f"Unsupported primitive type {self}")

    # @property
    # def model(self) -> Type:
    #     if self in [StandardCTypesEnum.UINT8, StandardCTypesEnum.INT8]:
    #         return int
    #     if self in [StandardCTypesEnum.UINT16, StandardCTypesEnum.INT16]:
    #         return int
    #     if self in [StandardCTypesEnum.UINT32, StandardCTypesEnum.INT32]:
    #         return int
    #     if self in [StandardCTypesEnum.UINT64, StandardCTypesEnum.INT64]:
    #         return int
    #     if self == StandardCTypesEnum.FLOAT:
    #         return float
    #     if self == StandardCTypesEnum.DOUBLE:
    #         return float
    #     if self == StandardCTypesEnum.CHAR:
    #         return str
    #     if self == StandardCTypesEnum.BOOL:
    #         return bool
    #     raise ValueError(f"Unsupported primitive type {self}")

    # def initialise_model(self, value: Any):
    #     if value is None:
    #         return None

    #     return self.model(value)

    @property
    def default_format(self) -> "CFormatEnum":
        if self in [
            StandardCTypesEnum.UINT8,
            StandardCTypesEnum.INT8,
            StandardCTypesEnum.UINT16,
            StandardCTypesEnum.INT16,
            StandardCTypesEnum.UINT32,
            StandardCTypesEnum.INT32,
        ]:
            return CFormatEnum.NUMBER
        elif self in [StandardCTypesEnum.FLOAT, StandardCTypesEnum.DOUBLE]:
            return CFormatEnum.DECIMAL
        elif self == StandardCTypesEnum.CHAR:
            return CFormatEnum.STRING
        elif self == StandardCTypesEnum.BOOL:
            return CFormatEnum.NUMBER

        raise ValueError(f"Unsupported primitive type {self}")

    @property
    def element_type(self) -> "StandardCTypesEnum":
        return self


class CFormatEnum(StrEnum):
    NUMBER = "number"
    DECIMAL = "decimal"
    STRING = "string"
    HEX = "hex"
    AUTO = "auto"

    @property
    def prefix(self) -> str:
        return "ODIN_ENCODING_"

    @property
    def odin_type_macro(self) -> str:
        return f"{self.prefix}{self.name}"

    # def odin_type_conv(self, primitive: StandardCTypesEnum, length: int | None) -> str:
    #     if self != CFormatEnum.AUTO:
    #         return self.odin_type

    #     if primitive in [
    #         StandardCTypesEnum.UINT8,
    #         StandardCTypesEnum.INT8,
    #         StandardCTypesEnum.UINT16,
    #         StandardCTypesEnum.INT16,
    #         StandardCTypesEnum.UINT32,
    #         StandardCTypesEnum.INT32,
    #     ]:
    #         return CFormatEnum.NUMBER.odin_type
    #     elif primitive in [StandardCTypesEnum.FLOAT, StandardCTypesEnum.DOUBLE]:
    #         return CFormatEnum.DECIMAL.odin_type
    #     elif primitive == StandardCTypesEnum.CHAR:
    #         return CFormatEnum.STRING.odin_type
    #     elif primitive == StandardCTypesEnum.BOOL:
    #         return CFormatEnum.NUMBER.odin_type
    #     else:
    #         raise ValueError(f"Unsupported primitive type {primitive}")
