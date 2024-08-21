# class CTypeEnum(StrEnum):
#     UINT8 = "uint8_t"
#     INT8 = "int8_t"
#     INT16 = "int16_t"
#     UINT16 = "uint16_t"
#     INT32 = "int32_t"
#     UINT32 = "uint32_t"
#     UINT64 = "uint64_t"
#     INT64 = "int64_t"
#     FLOAT = "float"
#     DOUBLE = "double"
#     CHAR = "char"
#     BOOL = "bool"

#     @property
#     def odin_type_define(self) -> str:
#         return f"ODIN_ELEMENT_TYPE_{self.name}"

#     def sizeof(self, length: int | None) -> str:
#         if length is None:
#             return f"sizeof({self.value})"
#         else:
#             return f"sizeof({self.value})*{length}"

#     def to_python_primitive(self, data: bytes) -> Union[int, float, str, bool]:
#         if self in [CTypeEnum.UINT8, CTypeEnum.INT8]:
#             return struct.unpack("b", data)[0]
#         if self in [CTypeEnum.UINT16, CTypeEnum.INT16]:
#             return struct.unpack("h", data)[0]
#         if self in [CTypeEnum.UINT32, CTypeEnum.INT32]:
#             return struct.unpack("i", data)[0]
#         if self in [CTypeEnum.UINT64, CTypeEnum.INT64]:
#             return struct.unpack("q", data)[0]
#         if self == CTypeEnum.FLOAT:
#             return struct.unpack("f", data)[0]
#         if self == CTypeEnum.DOUBLE:
#             return struct.unpack("d", data)[0]
#         if self == CTypeEnum.CHAR:
#             return struct.unpack("c", data)[0]
#         if self == CTypeEnum.BOOL:
#             return struct.unpack("?", data)[0]

#     def to_c_primitive(self, data: Union[int, float, str, bool]) -> bytes:
#         if self in [CTypeEnum.UINT8, CTypeEnum.INT8]:
#             return struct.pack("b", data)
#         if self in [CTypeEnum.UINT16, CTypeEnum.INT16]:
#             return struct.pack("h", data)
#         if self in [CTypeEnum.UINT32, CTypeEnum.INT32]:
#             return struct.pack("i", data)
#         if self in [CTypeEnum.UINT64, CTypeEnum.INT64]:
#             return struct.pack("q", data)
#         if self == CTypeEnum.FLOAT:
#             return struct.pack("f", data)
#         if self == CTypeEnum.DOUBLE:
#             return struct.pack("d", data)
#         if self == CTypeEnum.CHAR:
#             return struct.pack("c", data)
#         if self == CTypeEnum.BOOL:
#             return struct.pack("?", data)


# class CFormatEnum(StrEnum):
#     NUMBER = "number"
#     DECIMAL = "decimal"
#     STRING = "string"
#     HEX = "hex"
#     AUTO = "auto"

#     @property
#     def prefix(self) -> str:
#         return "ODIN_ENCODING_"

#     @property
#     def odin_type(self) -> str:
#         return f"{self.prefix}{self.name}"

#     def odin_type_conv(self, primitive: CTypeEnum, length: int | None) -> str:
#         if self != CFormatEnum.AUTO:
#             return self.odin_type

#         if primitive in [
#             CTypeEnum.UINT8,
#             CTypeEnum.INT8,
#             CTypeEnum.UINT16,
#             CTypeEnum.INT16,
#             CTypeEnum.UINT32,
#             CTypeEnum.INT32,
#         ]:
#             return CFormatEnum.NUMBER.odin_type
#         elif primitive in [CTypeEnum.FLOAT, CTypeEnum.DOUBLE]:
#             return CFormatEnum.DECIMAL.odin_type
#         elif primitive == CTypeEnum.CHAR:
#             return CFormatEnum.STRING.odin_type
#         elif primitive == CTypeEnum.BOOL:
#             return CFormatEnum.NUMBER.odin_type
#         else:
#             raise ValueError(f"Unsupported primitive type {primitive}")
