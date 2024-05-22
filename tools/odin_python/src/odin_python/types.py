from typing import Dict, List, Literal, Union

import csnake as cc
from csnake import CodeWriter, FormattedLiteral
from pydantic import BaseModel, Field, model_validator
from strenum import StrEnum

from .extensions import (
    EXENSIONS,
    ReferenceParameterExtensionModel,
    ValidationParameterExtensionModel,
)
from .utils.csnake_custom import StructVariable


class CTypeEnum(StrEnum):
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

    @property
    def odin_type_define(self) -> str:
        return f"ODIN_ELEMENT_TYPE_{self.name}"

    def sizeof(self, length: int | None) -> str:
        if length is None:
            return f"sizeof({self.value})"
        else:
            return f"sizeof({self.value})*{length}"


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
    def odin_type(self) -> str:
        return f"{self.prefix}{self.name}"

    def odin_type_conv(self, primitive: CTypeEnum, length: int | None) -> str:
        if self != CFormatEnum.AUTO:
            return self.odin_type

        if primitive in [
            CTypeEnum.UINT8,
            CTypeEnum.INT8,
            CTypeEnum.UINT16,
            CTypeEnum.INT16,
            CTypeEnum.UINT32,
            CTypeEnum.INT32,
        ]:
            return CFormatEnum.NUMBER.odin_type
        elif primitive in [CTypeEnum.FLOAT, CTypeEnum.DOUBLE]:
            return CFormatEnum.DECIMAL.odin_type
        elif primitive == CTypeEnum.CHAR:
            return CFormatEnum.STRING.odin_type
        elif primitive == CTypeEnum.BOOL:
            return CFormatEnum.NUMBER.odin_type
        else:
            raise ValueError(f"Unsupported primitive type {primitive}")
