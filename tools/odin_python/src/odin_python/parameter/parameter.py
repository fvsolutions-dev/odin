from ..data_types.type_registry import DataType, RegularCDataType, TypeRegistry
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from odin_python.utils.string import escape_string
from typing import Any, Dict

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


class BaseParameterModel(BaseModel, ABC):
    model_config = ConfigDict(extra="forbid")

    # Name Set by the post_load_resolve method
    _name: str = PrivateAttr()
    _parent: "BaseParameterModel|None" = PrivateAttr(default=None)

    local_id: int = Field(description="Local id of the parameter")
    description: str | None = Field(
        description="Description of the parameter", default=None
    )

    @property
    def resolved_description(self) -> str:
        return self.description if self.description else "No description"

    def post_load_resolve(
        self,
        parent: "BaseParameterModel | None",
        name: str,
        type_registry: TypeRegistry,
    ):
        del type_registry
        self._parent = parent
        self._name = name

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
        return cc.Variable(
            name=self._name,
            primitive=ODIN_PARAMETER_TYPE,
            value={
                "index": cc.TextModifier(f"0x{self.global_id:08X}"),
                "data": cc.TextModifier(f"&{self.reference}"),
                "size": cc.TextModifier(f"sizeof({self._resolved_type.c_typename})"),
                "name": self._name,
                "description": escape_string(self.resolved_description),
            },  # type: ignore
        )

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable | None:
        return None


class ParameterModel(BaseParameterModel):
    # Reference to the parent model if any

    # Primitive, must be mapped to a known type
    type: str = Field(description="Primitive type of the parameter")

    _resolved_type: DataType = PrivateAttr()
    default: Any = Field(description="Default value of the parameter")
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
        # permission_flags = self._access_configuration.get_permission_flags()
        assert isinstance(self._resolved_type, RegularCDataType)
        return cc.Variable(
            name=self._name,
            primitive=ODIN_PARAMETER_TYPE,
            value={
                "index": cc.TextModifier(f"0x{self.global_id:08X}"),
                # "access": cc.TextModifier(
                #     "|".join(permission_flags) if permission_flags else "0"
                # ),
                # "format": cc.TextModifier(
                #     primitive_type.default_format.odin_type_macro
                #     if self.format == CFormatEnum.AUTO
                #     else self.format.odin_type_macro
                # ),
                # "type": cc.TextModifier(primitive_type.element_type.odin_type_macro),
                "data": cc.TextModifier(f"&{self._data_storage_reference}"),
                "size": cc.TextModifier(f"sizeof({self._resolved_type.c_typename})"),
                "name": self._name,
                "description": escape_string(self.resolved_description),
            },  # type: ignore
        )

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

    # def primitive_type(self, types) -> StandardCTypesEnum | GenericDataType:
    #     if isinstance(self.type, StandardCTypesEnum):
    #         return self.type
    #     return types[self.type]

    # def init_children(
    #     self,
    #     parent: "ParameterGroupModel|ParameterStoreModel",
    #     name: str,
    #     access_permissions: AccessConfigurations | AccessConfigurationType,
    # ):
    #     self._name = name
    #     self._parent = parent
    #     self._access_configuration = AccessConfigurations.inherit(
    #         access_permissions, self.access_permissions
    #     )


class BaseParameterGroupModel(BaseParameterModel):
    children: "Dict[str, ParameterGroupModel|ParameterModel|ReferenceParameterModel]"

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
            elif isinstance(child, ParameterModel) or isinstance(
                child, ReferenceParameterModel
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
            elif isinstance(child, ParameterModel):
                struct.add_variable(child.to_c_initialiser(child._name, child.type, ""))
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
        for child_name, child in self.children.items():
            initialiser = child.to_c_initialiser(name, type_name, name)

            if initialiser is not None:
                values[child_name] = initialiser.value

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

    def to_c_initialiser(
        self, name: str, type_name: str, absolute_reference: str = ""
    ) -> cc.Variable:
        values = {}
        for child_name, child in self.children.items():
            initialiser = child.to_c_initialiser(name, type_name, name)

            if initialiser is not None:
                values[child_name] = initialiser.value

        return cc.Variable(
            name=name,
            primitive=type_name,
            value=values,  # type: ignore
        )
