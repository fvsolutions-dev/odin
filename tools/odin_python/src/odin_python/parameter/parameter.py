from abc import ABC, abstractmethod
from ctypes import Union
from typing import Annotated, Any, Dict, List

import csnake as cc
from odin_python.parameter.access_control import AccessControlCollection
from odin_python.utils.csnake_custom import StructVariable
from pydantic import BaseModel, ConfigDict, Discriminator, Field, PrivateAttr, Tag

from ..data_types.type_registry import DataType, RegularCDataType, TypeRegistry
from ..extensions import Extensions
from ..generator.model import (
    ODIN_ArrayModel,
    ODIN_ParameterGroupModel,
    ODIN_ParameterModel,
)

MAX_ID_SIZE = 32


class BaseParameterModel(BaseModel, ABC):
    """The base parameter model, is an abstract class that all parameter models inherit from

    It contains the basic properties and methods that all parameter models should have
    """

    model_config = ConfigDict(extra="forbid")

    # Name of the parameter, set by the post_load_resolve method
    _name: str = PrivateAttr()

    # Reference to the parent of the parameter, set by the post_load_resolve method
    _parent: "BaseParameterModel|None" = PrivateAttr(default=None)

    local_id: int = Field(
        description="Local id of the parameter, unique within the parent"
    )

    description: str | None = Field(
        description="Description of the parameter, optional", default=None
    )

    access_control: AccessControlCollection = Field(
        description="Access control configuration for the parameter",
        default_factory=AccessControlCollection.empty,
    )

    extensions: List[Extensions] | None = Field(description="Extensions", default=None)

    def post_load_resolve(
        self,
        parent: "BaseParameterModel | None",
        name: str,
        type_registry: TypeRegistry,
    ):
        """Post load resolve method, must to be called after the model is created"""

        del type_registry  # type_registry is not used here
        self._parent = parent
        self._name = name
        self.access_control._parent = self

    @property
    def resolved_description(self) -> str:
        """Returns the description of the parameter, if not set returns a default value"""
        return self.description if self.description else "No description"

    @property
    def global_id(self) -> int:
        """Calculates the global id of the parameter, by going up the tree"""

        if self._parent is None:
            return self.local_id

        if isinstance(self._parent, RootParameterModel):
            return self.local_id << (MAX_ID_SIZE - self.global_shift)

        elif isinstance(self._parent, ParameterGroupModel):
            return self._parent.global_id | (
                self.local_id << (MAX_ID_SIZE - self.global_shift)
            )
        else:
            raise ValueError("Parent is not a ParameterGroupModel")

    @property
    def global_shift(self) -> int:
        """Adds the shift of all the parents to upstream"""

        if self._parent is None:
            return 0

        if isinstance(self._parent, RootParameterModel):
            return self._parent.id_space_shift

        elif isinstance(self._parent, ParameterGroupModel):
            return self._parent.global_shift + self._parent.id_space_shift

        else:
            raise ValueError("Parent is not a ParameterGroupModel")

    @abstractmethod
    def to_c_odin_parameter_initialiser(
        self, absolute_reference: str, **kwargs
    ) -> cc.Variable:
        """Returns the C initialiser for the parameter"""

    @abstractmethod
    def to_ram_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable | None:
        """Returns the ram initialiser for the parameter"""


class ParameterModel(BaseParameterModel):
    """Parameter model, represents a single parameter"""

    type: str = Field(description="Primitive type of the parameter")

    # The type this parameter resolves to, set by the post_load_resolve method
    _resolved_type: DataType = PrivateAttr()

    # Default value of the parameter, it not set it will use the default value of the primitive type
    default: Any = Field(description="Default value of the parameter")

    # Reference to the variable which stores the data
    _data_storage_reference: str | None = PrivateAttr(default=None)

    # Reference to the odin parameter
    _parameter_storage_reference: str | None = PrivateAttr(default=None)

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

    def to_ram_initialiser(
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

    def to_c_odin_parameter_initialiser(
        self, absolute_reference: str, **kwargs
    ) -> cc.Variable:
        """Returns the odin C initialiser for the parameter"""

        # permission_flags = self._access_configuration.get_permission_flags()

        assert isinstance(self._resolved_type, RegularCDataType)

        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set, call to_c_initialiser first to set the reference"

        # Store a reference to the parameter name
        self._parameter_storage_reference = f"{absolute_reference}.{self._name}"

        parameter = ODIN_ParameterModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
        )
        return parameter.variable


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

    def to_ram_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> None:
        """No need to initialise a ram storage entry because the parameter is referenced"""
        return None

    def to_c_odin_parameter_initialiser(
        self, absolute_reference: str, **kwargs
    ) -> cc.Variable:
        """Returns the odin C initialiser for the parameter"""

        assert isinstance(self._resolved_type, RegularCDataType)

        self._parameter_storage_reference = f"{absolute_reference}.{self._name}"

        parameter = ODIN_ParameterModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self.reference,
            name=self._name,
            description=self.resolved_description,
        )

        return parameter.variable


class ArrayParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the element in the array")
    default: Any | None = Field(
        description="Default value of the parameter", default=None
    )
    elements: int = Field(description="Number of elements in the array")

    _resolved_type: DataType = PrivateAttr()

    # Reference to the variable which stores the data
    _data_storage_reference: str | None = PrivateAttr(default=None)

    # Reference to the odin parameter
    _parameter_storage_reference: str | None = PrivateAttr(default=None)

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_ram_initialiser(
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
            self._name, self.default if self.default else [], [self.elements]
        )

    def to_c_odin_parameter_initialiser(
        self, absolute_reference: str, **kwargs
    ) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)
        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set"

        self._parameter_storage_reference = f"{absolute_reference}.{self._name}"

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.elements,
        )
        return parameter.variable


class VectorParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the element in the array")
    default: List[Any] | None = Field(
        description="Default value of the parameter", default=None
    )
    max_elements: int = Field(description="Number of elements in the array")

    _resolved_type: DataType = PrivateAttr()

    # Reference to the variable which stores the data
    _data_storage_reference: str | None = PrivateAttr(default=None)

    # Reference to the odin parameter
    _parameter_storage_reference: str | None = PrivateAttr(default=None)

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

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
                primitive="size_t",
                value=len(self.default) if self.default else 0,  # type: ignore
            ),
        )

        struct.add_variable(
            self._resolved_type.to_c_array_initialiser(
                "data", self.default, [self.max_elements]
            )
        )
        return struct

    def to_ram_initialiser(
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

    def to_c_odin_parameter_initialiser(
        self, absolute_reference: str, **kwargs
    ) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)

        assert (
            self._data_storage_reference is not None
        ), "Data storage reference is not set"

        self._parameter_storage_reference = f"{absolute_reference}.{self._name}"

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self._data_storage_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.max_elements,
            fixed_size=False,
        )
        return parameter.variable

    # def to_c_odin_parameter_initialiser(self, **kwargs) -> cc.Variable:
    #     # permission_flags = self._access_configuration.get_permission_flags()
    #     assert isinstance(self._resolved_type, RegularCDataType)parameters
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


def get_discriminator_value(v: Any) -> str:
    if isinstance(v, dict):
        if "children" in v:
            val = "group"
        elif "reference" in v:
            val = "reference"
        elif "elements" in v:
            val = "array"
        elif "max_elements" in v:
            val = "vector"
        else:
            val = "parameter"
    else:
        if isinstance(v, ParameterGroupModel):
            val = "group"
        elif isinstance(v, ReferenceParameterModel):
            val = "reference"
        elif isinstance(v, VectorParameterModel):
            val = "vector"
        elif isinstance(v, ArrayParameterModel):
            val = "array"
        elif isinstance(v, ParameterModel):
            val = "parameter"
        else:
            raise ValueError(f"Unknown type {type(v)}")

    return val


class BaseParameterGroupModel(BaseParameterModel):
    children: """Dict[
        str,
        Annotated[
            Annotated[ParameterModel, Tag("parameter")]
            | Annotated[ReferenceParameterModel, Tag("reference")]
            | Annotated[ArrayParameterModel, Tag("array")]
            | Annotated[VectorParameterModel, Tag("vector")]
            | Annotated[ParameterGroupModel, Tag("group")],
            Discriminator(get_discriminator_value)
        ]
    ]"""
    id_space_shift: int = Field(description="Number of bits to shift the children ids")

    # Reference to the odin parameter
    _parameter_storage_reference: str | None = PrivateAttr(default=None)

    # _group_storage_reference: str | None = PrivateAttr(default=None)

    def post_load_resolve(
        self,
        parent: BaseParameterModel | None,
        name: str,
        type_registry: TypeRegistry,
    ):
        super().post_load_resolve(parent, name, type_registry)
        for child_name, child in self.children.items():
            child.post_load_resolve(self, child_name, type_registry)

        self.validate_local_id()

        # Validate ids
        global_id_map = self.build_global_id_map()

    def to_c_odin_parameter_initialiser(
        self,
        *,
        absolute_reference: str,
        param_name: str | None = None,
        type_name: str | None = None,
        **kwargs,
    ) -> cc.Variable:
        if absolute_reference == "":
            absolute_reference = self._name
        else:
            absolute_reference = f"{absolute_reference}.{self._name}"

        return cc.Variable(
            name=param_name if param_name else "UNKNOWN_NAME",
            primitive=type_name if type_name else "UKNOWN_TYPE",
            value={
                parameter_name: parameter.to_c_odin_parameter_initialiser(
                    absolute_reference=absolute_reference
                ).value
                for parameter_name, parameter in self.children.items()  # type: ignore
            },
        )

    def to_c_odin_parameter_group_initialiser(
        self, *, param_name: str, **kwargs
    ) -> List[cc.Variable]:
        variables = []

        for parameter_name, parameter in self.children.items():
            if isinstance(parameter, ParameterGroupModel):
                variables.extend(
                    parameter.to_c_odin_parameter_group_initialiser(
                        param_name=f"{param_name}_{parameter_name}"
                    )
                )

        # self._group_storage_reference = self._name
        self._parameter_storage_reference = param_name
        parameters_references = []
        for parameter_name, parameter in self.children.items():
            assert (
                parameter._parameter_storage_reference is not None
            ), "Parameter storage reference is not set"
            parameters_references.append(parameter._parameter_storage_reference)

        variables.append(
            ODIN_ParameterGroupModel(
                param_name=param_name,
                name=self._name,
                description=self.resolved_description,
                global_id=self.global_id,
                id_space_shift=self.id_space_shift,
                parameters_references=parameters_references,
            ).variable
        )

        return variables

    def one_line_summary(self, level=0):
        val = f"{level * '  '}{self._name} (0x{self.global_id:08X})"
        for child in self.children.values():
            val += f"\n{child.one_line_summary(level + 1)}"
        return val

    def to_odin_parameter_typedef(
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
                struct.add_struct(child.to_odin_parameter_typedef())

            elif (
                isinstance(child, ParameterModel)
                or isinstance(child, ReferenceParameterModel)
                or isinstance(child, VectorParameterModel)
                or isinstance(child, ArrayParameterModel)
            ):
                # Set the storqage reference to UNSET to not trigger an error when creating the initialiser
                if not isinstance(child, ReferenceParameterModel):
                    child._data_storage_reference = "UNSET"

                struct.add_variable(
                    child.to_c_odin_parameter_initialiser(absolute_reference="UNKNOWN")
                )

            else:
                raise ValueError("Unknown type")

        return struct

    def to_ram_typedef(
        self,
        type_name: str | None = None,
    ) -> cc.Struct:
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=self._name, typedef=False)

        for child in self.children.values():
            if isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_ram_typedef())

            elif isinstance(child, VectorParameterModel):
                child.to_ram_initialiser(child._name, child.type, "")
                struct.add_struct(child.to_ram_struct())

            elif isinstance(child, ParameterModel) or isinstance(
                child, ArrayParameterModel
            ):
                variable = child.to_ram_initialiser(child._name, child.type, "")
                if variable:
                    struct.add_variable(variable)

            elif isinstance(child, ReferenceParameterModel):
                pass

            else:
                raise ValueError("Unknown type")

        return struct

    def to_ram_initialiser(
        self, name: str, type_name: str, absolute_reference: str
    ) -> cc.Variable:
        absolute_reference = f"{absolute_reference}.{self._name}"

        values = {}
        for child in self.children.values():
            initialiser = child.to_ram_initialiser(name, type_name, absolute_reference)

            if initialiser:
                values[initialiser.name] = initialiser.value

        return cc.Variable(
            name=self._name,
            primitive="UNKNOWN PRIMITIVE",
            value=values,  # type: ignore
        )

    def validate_local_id(self):
        local_id_map = {}
        for child in self.children.values():
            if child.local_id in local_id_map:
                raise ValueError(f"Id conflict found: {child.local_id} in {self._name}")
            else:
                local_id_map[child.local_id] = child

            # check if local id respects bit shift
            if child.local_id >= (1 << self.id_space_shift):
                raise ValueError(
                    f"Local id {child.local_id} is larger than the id shift {self.id_space_shift} in {self._name}"
                )

            if isinstance(child, BaseParameterGroupModel):
                child.validate_local_id()

    def build_global_id_map(self) -> Dict[int, BaseParameterModel]:
        """Builds a map of the global ids to the parameters"""

        global_id_map: Dict[int, BaseParameterModel] = {self.global_id: self}

        for child in self.children.values():
            if isinstance(child, BaseParameterGroupModel):
                global_id_map.update(child.build_global_id_map())

            elif isinstance(child, BaseParameterModel):
                global_id_map[child.global_id] = child

        return global_id_map


class ParameterGroupModel(BaseParameterGroupModel):
    pass


class RootParameterModel(BaseParameterGroupModel):
    local_id: int = 0

    def dump_json(self):
        return self.model_dump_json(indent=2)

    def to_ram_initialiser(
        self, name: str, type_name: str, absolute_reference: str = ""
    ) -> cc.Variable:
        values = {}
        for child in self.children.values():
            initialiser = child.to_ram_initialiser(name, type_name, name)

            if initialiser:
                values[initialiser.name] = initialiser.value

        return cc.Variable(
            name=name,
            primitive=type_name,
            value=values,  # type: ignore
        )

    def to_access_control_header(self) -> List[str]:
        # todo possible move this into acces contol info?
        assert self.access_control is not None, "Access control info is not set"
        groups = self.access_control.get_access_group_ids()

        defines = []
        for id, name in groups.items():
            defines.append(f"#define ODIN_ACCESS_{name.upper()} ODIN_ACCESS_GROUP_{id}")

        return defines
