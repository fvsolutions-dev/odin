from enum import Enum
from ..data_types.type_registry import DataType, RegularCDataType, TypeRegistry
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from odin_python.utils.string import escape_string
from typing import Any, Dict, List

# from .models import AccessOptionsGenerator, MainModel, DeviceGroupModel
# from ..data_types.custom_enum import EnumeratorDataType
# from ..data_types.custom_structure import GenericDataType, StructureDataType
# from ..data_types.standard_types import CFormatEnum, StandardCTypesEnum
import csnake as cc  # type: ignore
from odin_python.utils.csnake_custom import StructVariable

# from ..extensions import (
#     EXENSIONS,
#     MappingParameterExtensionModel,
# )
from abc import ABC, abstractmethod

ODIN_PARAMETER_TYPE = "ODIN_parameter_t"
ODIN_ARRAY_PARAMETER_TYPE = "ODIN_array_t"
ODIN_VECTOR_PARAMETER_TYPE = "ODIN_vector_t"


class BaseParameterModel(BaseModel, ABC):
    model_config = ConfigDict(extra="forbid")

    # Name of the parameter, set by the post_load_resolve method
    _name: str = PrivateAttr()

    # Parent of the parameter, set by the post_load_resolve method
    _parent: "BaseParameterModel|None" = PrivateAttr(default=None)

    # Local id of the parameter
    local_id: int = Field(description="Local id of the parameter")

    # Description of the parameter, optional
    description: str | None = Field(
        description="Description of the parameter", default=None
    )

    def post_load_resolve(
        self,
        parent: "BaseParameterModel | None",
        name: str,
        type_registry: TypeRegistry,
    ):
        """Post load resolve method, needs to be called after the model is initialized"""
        del type_registry
        self._parent = parent
        self._name = name

    @property
    def resolved_description(self) -> str:
        """Returns the description of the parameter, if not set returns 'No description'"""
        return self.description if self.description else "No description"

    @property
    def global_id(self) -> int:
        """Returns the global id of the parameter"""
        if self._parent is None:
            return self.local_id

        if isinstance(self._parent, ParameterGroupModel):
            return self._parent.global_id << self._parent.id_shift | self.local_id
        elif isinstance(self._parent, RootParameterModel):
            return self.local_id
        else:
            raise ValueError("Parent is not a ParameterGroupModel")

    @abstractmethod
    def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable: ...

    @abstractmethod
    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable | None: ...


class ODIN_TypeEnum(Enum):
    ODIN_TYPE_PARAMETER = "ODIN_TYPE_PARAMETER"
    ODIN_TYPE_ARRAY = "ODIN_TYPE_ARRAY"
    ODIN_TYPE_VECTOR = "ODIN_TYPE_VECTOR"


class ODIN_ElementTypeEnum(Enum):
    ODIN_ELEMENT_TYPE_BOOL = "ODIN_ELEMENT_TYPE_BOOL"
    ODIN_ELEMENT_TYPE_HEX = "ODIN_ELEMENT_TYPE_HEX"
    ODIN_ELEMENT_TYPE_UINT8 = "ODIN_ELEMENT_TYPE_UINT8"
    ODIN_ELEMENT_TYPE_UINT16 = "ODIN_ELEMENT_TYPE_UINT16"
    ODIN_ELEMENT_TYPE_UINT32 = "ODIN_ELEMENT_TYPE_UINT32"
    ODIN_ELEMENT_TYPE_UINT64 = "ODIN_ELEMENT_TYPE_UINT64"
    ODIN_ELEMENT_TYPE_INT8 = "ODIN_ELEMENT_TYPE_INT8"
    ODIN_ELEMENT_TYPE_INT16 = "ODIN_ELEMENT_TYPE_INT16"
    ODIN_ELEMENT_TYPE_INT32 = "ODIN_ELEMENT_TYPE_INT32"
    ODIN_ELEMENT_TYPE_INT64 = "ODIN_ELEMENT_TYPE_INT64"
    ODIN_ELEMENT_TYPE_FLOAT32 = "ODIN_ELEMENT_TYPE_FLOAT32"
    ODIN_ELEMENT_TYPE_FLOAT64 = "ODIN_ELEMENT_TYPE_FLOAT64"
    ODIN_ELEMENT_TYPE_CHAR = "ODIN_ELEMENT_TYPE_CHAR"
    ODIN_ELEMENT_TYPE_CUSTOM = "ODIN_ELEMENT_TYPE_CUSTOM"

    @classmethod
    def from_c_type(cls, c_type: str) -> "ODIN_ElementTypeEnum":
        if c_type == "bool":
            return cls.ODIN_ELEMENT_TYPE_BOOL
        if c_type == "uint8_t":
            return cls.ODIN_ELEMENT_TYPE_UINT8
        if c_type == "uint16_t":
            return cls.ODIN_ELEMENT_TYPE_UINT16
        if c_type == "uint32_t":
            return cls.ODIN_ELEMENT_TYPE_UINT32
        if c_type == "uint64_t":
            return cls.ODIN_ELEMENT_TYPE_UINT64
        if c_type == "int8_t":
            return cls.ODIN_ELEMENT_TYPE_INT8
        if c_type == "int16_t":
            return cls.ODIN_ELEMENT_TYPE_INT16
        if c_type == "int32_t":
            return cls.ODIN_ELEMENT_TYPE_INT32
        if c_type == "int64_t":
            return cls.ODIN_ELEMENT_TYPE_INT64
        if c_type == "float":
            return cls.ODIN_ELEMENT_TYPE_FLOAT32
        if c_type == "double":
            return cls.ODIN_ELEMENT_TYPE_FLOAT64
        if c_type == "char":
            return cls.ODIN_ELEMENT_TYPE_CHAR
        return cls.ODIN_ELEMENT_TYPE_CUSTOM


class ODIN_ParameterModel(BaseModel):
    access_group: int = Field(description="Access group")
    index: int = Field(description="Index of the parameter")
    data: str = Field(description="Reference to the data")
    type: DataType = Field(description="Resolved type of the parameter")
    name: str = Field(description="Name of the parameter")
    description: str = Field(description="Description of the parameter")
    extension: str | None = Field(description="Extension info", default=None)

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
                "index": cc.TextModifier(f"0x{self.index:08X}"),
                "size": cc.TextModifier(f"sizeof({self.type.c_typename})"),
                "data": cc.TextModifier(f"&{self.data}"),
                "name": self.name,
                "description": escape_string(self.description),
                "extension": cc.TextModifier(self.extension)
                if self.extension
                else cc.TextModifier("NULL"),
            },  # type: ignore
        )


class ODIN_ArrayModel(BaseModel):
    access_group: int = Field(description="Access group")
    index: int = Field(description="Index of the parameter")
    data: str = Field(description="Reference to the data")
    type: DataType = Field(description="Resolved type of the parameter")
    name: str = Field(description="Name of the parameter")
    description: str = Field(description="Description of the parameter")
    extension: str | None = Field(description="Extension info", default=None)
    num_elements: int = Field(description="Number of elements in the array")
    fixed_size: bool = Field(description="Fixed size of the array", default=True)

    @property
    def variable(self) -> cc.Variable:
        assert isinstance(self.type, RegularCDataType)

        return cc.Variable(
            name=self.name,
            primitive=ODIN_ARRAY_PARAMETER_TYPE
            if self.fixed_size
            else ODIN_VECTOR_PARAMETER_TYPE,
            value={
                "parameter": {
                    "odin_type": cc.TextModifier(
                        str(ODIN_TypeEnum.ODIN_TYPE_ARRAY.value)
                        if self.fixed_size
                        else str(ODIN_TypeEnum.ODIN_TYPE_VECTOR.value)
                    ),
                    "element_type": cc.TextModifier(
                        str(
                            ODIN_ElementTypeEnum.from_c_type(self.type.c_typename).value
                        )
                    ),
                    "flags": cc.TextModifier(str(self.access_group)),
                    "index": cc.TextModifier(f"0x{self.index:08X}"),
                    "size": cc.TextModifier(f"sizeof({self.type.c_typename})"),
                    "data": cc.TextModifier(f"&{self.data}"),
                    "name": self.name,
                    "description": escape_string(self.description),
                    "extension": cc.TextModifier(self.extension)
                    if self.extension
                    else cc.TextModifier("NULL"),
                },
                "max_elements": cc.TextModifier(str(self.num_elements)),
            },  # type: ignore
        )


class ParameterModel(BaseParameterModel):
    """Parameter model, represents a single parameter"""

    type: str = Field(description="Primitive type of the parameter")

    # The type this parameter resolves to, set by the post_load_resolve method
    _resolved_type: DataType = PrivateAttr()

    # Default value of the parameter, it not set it will use the default value of the primitive type
    default: Any = Field(description="Default value of the parameter")

    # Referece to the variable which stores the data
    _data_storage_reference: str | None = PrivateAttr(default=None)

    # format: CFormatEnum = Field(
    #     default=CFormatEnum.AUTO,
    #     description="The format of the data, represents the way the data has to be displayed. If set to 'auto', the format will be determined based on the primitive type.",
    # )

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
        """Returns the C initialiser for the parameter"""

        # permission_flags = self._access_configuration.get_permission_flags()

        assert isinstance(self._resolved_type, RegularCDataType)

        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set"

        parameter = ODIN_ParameterModel(
            type=self._resolved_type,
            access_group=0,
            index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
        )
        return parameter.variable

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable:
        """Returns the C initialiser for the parameter

        Example:
        ```
        uint32_t my_parameter = 0;
        ```
        """

        self._data_storage_reference = f"{absolute_reference}.{self._name}"

        assert isinstance(self._resolved_type, RegularCDataType)
        return self._resolved_type.to_c_initialiser(self._name, self.default)


class ReferenceParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the parameter")
    _resolved_type: DataType = PrivateAttr()
    reference: str = Field(description="Reference to the point in memory")

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)
        parameter = ODIN_ParameterModel(
            type=self._resolved_type,
            access_group=0,
            index=self.global_id,
            data=self.reference,
            name=self._name,
            description=self.resolved_description,
        )

        return parameter.variable

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> None:
        return None


class ArrayParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the element in the array")
    default: Any | None = Field(
        description="Default value of the parameter", default=None
    )
    elements: int = Field(description="Number of elements in the array")

    _resolved_type: DataType = PrivateAttr()
    _data_storage_reference: str | None = PrivateAttr(default=None)

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)
        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set"

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=0,
            index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.elements,
        )
        return parameter.variable

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable:
        """Returns the C initialiser for the parameter

        Example:
        ```
        uint32_t my_parameter = 0;
        ```
        """

        self._data_storage_reference = f"{absolute_reference}.{self._name}"

        assert isinstance(self._resolved_type, RegularCDataType)
        return self._resolved_type.to_c_array_initialiser(
            self._name, self.default, [self.elements]
        )


class VectorParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the element in the array")
    default: List[Any] | None = Field(
        description="Default value of the parameter", default=None
    )
    max_elements: int = Field(description="Number of elements in the array")

    _resolved_type: DataType = PrivateAttr()
    _data_storage_reference: str | None = PrivateAttr(default=None)

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)

        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set"

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=0,
            index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.max_elements,
            fixed_size=False,
        )
        return parameter.variable

    # def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
    #     # permission_flags = self._access_configuration.get_permission_flags()
    #     assert isinstance(self._resolved_type, RegularCDataType)
    #     return cc.Variable(
    #         name=self._name,
    #         primitive=ODIN_VECTOR_PARAMETER_TYPE,
    #         value={
    #             "index": cc.TextModifier(f"0x{self.global_id:08X}"),
    #             "max_elements": cc.TextModifier(str(self.max_elements)),
    #             "data": cc.TextModifier(f"&{self._data_storage_reference}"),
    #             "size": cc.TextModifier(f"sizeof({self._resolved_type.c_typename})"),
    #             "name": self._name,
    #             "description": escape_string(self.resolved_description),
    #         },  # type: ignore
    #     )

    def to_ram_struct(
        self,
        type_name: str | None = None,
    ) -> cc.Struct:
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=self._name, typedef=False)

        struct.add_variable(
            cc.Variable(
                name="num_elements",
                primitive="uint16_t",
                value=len(self.default) if self.default else 0,  # type: ignore
            ),
        )

        struct.add_variable(
            self._resolved_type.to_c_array_initialiser(
                "data", self.default, [self.max_elements]
            )
        )

        return struct

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable:
        self._data_storage_reference = f"{absolute_reference}.{self._name}"
        data = self._resolved_type.to_c_array_initialiser(
            self._name, self.default, [self.max_elements]
        )

        return cc.Variable(
            name=self._name,
            primitive="UNKNOWN PRIMITIVE",
            value={"data": data.value, "num_elements": len(self.default)},  # type: ignore
        )


class BaseParameterGroupModel(BaseParameterModel):
    children: "Dict[str, ParameterGroupModel|ParameterModel|ReferenceParameterModel|ArrayParameterModel|VectorParameterModel]"

    def post_load_resolve(
        self,
        parent: BaseParameterModel | None,
        name: str,
        type_registry: TypeRegistry,
    ):
        super().post_load_resolve(parent, name, type_registry)
        for child_name, child in self.children.items():
            child.post_load_resolve(self, child_name, type_registry)

    def to_c_odin_parameter_initialiser(
        self, *, param_name: str | None = None, type_name: str | None = None, **kwargs
    ) -> cc.Variable:
        return cc.Variable(
            name=param_name if param_name else "UNKNOWN_NAME",
            primitive=type_name if type_name else "UKNOWN_TYPE",
            value={
                parameter_name: parameter.to_c_odin_parameter_initialiser().value
                for parameter_name, parameter in self.children.items()  # type: ignore
            },
        )

    def one_line_summary(self, level=0):
        val = f"{level * '  '}{self._name} (0x{self.global_id:08X})"
        for child in self.children.values():
            val += f"\n{child.one_line_summary(level+1)}"
        return val

    def to_recursive_odin_typedef(
        self,
        type_name: str | None = None,
    ) -> cc.Struct:
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=self._name, typedef=False)
        # Create the data structures for groups
        for child in self.children.values():
            if isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_recursive_odin_typedef())

            elif (
                isinstance(child, ParameterModel)
                or isinstance(child, ReferenceParameterModel)
                or isinstance(child, VectorParameterModel)
                or isinstance(child, ArrayParameterModel)
            ):
                struct.add_variable(child.to_c_odin_parameter_initialiser())

            else:
                raise ValueError("Unknown type")

        return struct

    def to_ram_struct(
        self,
        type_name: str | None = None,
    ) -> cc.Struct:
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=self._name, typedef=False)

        for child in self.children.values():
            if isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_ram_struct())

            elif isinstance(child, VectorParameterModel):
                child.to_c_initialiser(child._name, child.type, "")
                struct.add_struct(child.to_ram_struct())

            elif isinstance(child, ParameterModel) or isinstance(
                child, ArrayParameterModel
            ):
                variable = child.to_c_initialiser(child._name, child.type, "")
                if variable:
                    struct.add_variable(variable)

            elif isinstance(child, ReferenceParameterModel):
                pass

            else:
                raise ValueError("Unknown type")

        return struct

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable:
        absolute_reference = f"{absolute_reference}.{self._name}"

        values = {}
        for child in self.children.values():
            initialiser = child.to_c_initialiser(name, type_name, name)

            if initialiser:
                values[initialiser.name] = initialiser.value

        return cc.Variable(
            name=self._name,
            primitive="UNKNOWN PRIMITIVE",
            value=values,  # type: ignore
        )


class ParameterGroupModel(BaseParameterGroupModel):
    id_shift: int = Field(description="Number of bits to shift the local id", default=0)


class RootParameterModel(BaseParameterGroupModel):
    local_id: int = 0

    def dump_json(self):
        return self.model_dump_json(indent=2)

    def to_c_value(
        self, name: str, type_name: str, absolute_reference: str = ""
    ) -> cc.Variable:
        values = {}
        for child in self.children.values():
            initialiser = child.to_c_initialiser(name, type_name, name)

            if initialiser:
                values[initialiser.name] = initialiser.value

        return cc.Variable(
            name=name,
            primitive=type_name,
            value=values,  # type: ignore
        )
