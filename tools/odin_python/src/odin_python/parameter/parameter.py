from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated, Any, Dict, List

import csnake as cc
from pydantic import BaseModel, ConfigDict, Discriminator, Field, PrivateAttr, Tag

from odin_python.parameter.access_control import AccessControlCollection
from odin_python.utils.csnake_custom import StructVariable

from ..data_types.type_registry import DataType, RegularCDataType, TypeRegistry
from ..extensions import Extensions
from ..generator.model import (
    ODIN_ArrayModel,
    ODIN_ParameterGroupModel,
    ODIN_ParameterModel,
)

MAX_ID_SIZE = 32


@dataclass
class C_Names:
    objects_type: str
    objects_name: str
    variables_type: str
    variables_name: str
    groups_name: str


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

    # Reference to the variable which stores the data
    _absolute_variable_reference: str | None = PrivateAttr(default=None)

    # Reference to the odin parameter, which represents the parameter in the odin runtime
    _absolute_object_reference: str | None = PrivateAttr(default=None)

    @abstractmethod
    def to_object_initialiser(self) -> cc.Variable:
        """Returns the C initialiser for the parameter"""

    @abstractmethod
    def to_variable_initialiser(self) -> cc.Variable | None:
        """Returns the ram initialiser for the parameter"""

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

    def initialise_types(self):
        assert self._parent is not None, "Parent is not set"

        self._absolute_variable_reference = (
            f"{self._parent._absolute_variable_reference}.{self._name}"
        )
        self._absolute_object_reference = (
            f"{self._parent._absolute_object_reference}.{self._name}"
        )

        if isinstance(self, BaseParameterGroupModel):
            self._absolute_group_reference = (
                f"{self._parent._absolute_group_reference}_{self._name}"
            )

            # If the parent is a group, then the variable reference is the parent name
            for child in self.children.values():
                child.initialise_types()

    @property
    def absolute_variable_reference(self) -> str:
        assert (
            self._absolute_variable_reference is not None
        ), "Variable reference is not set"
        return self._absolute_variable_reference

    @property
    def absolute_object_reference(self) -> str:
        assert (
            self._absolute_object_reference is not None
        ), "Object reference is not set"
        return self._absolute_object_reference

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

    @property
    def root(self) -> "RootParameterModel":
        """Returns the root of the tree"""

        if self._parent is None:
            assert isinstance(self, RootParameterModel), "Root is not set"
            return self

        if isinstance(self._parent, RootParameterModel):
            return self._parent

        return self._parent.root


class ParameterModel(BaseParameterModel):
    """Parameter model, represents a single parameter"""

    type: str = Field(description="Primitive type of the parameter")

    # The type this parameter resolves to, set by the post_load_resolve method
    _resolved_type: DataType = PrivateAttr()

    # Default value of the parameter, it not set it will use the default value of the primitive type
    default: Any = Field(description="Default value of the parameter")

    extensions: List[Extensions] | None = Field(
        description="Extensions of the parameter", default=None
    )

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_variable_initialiser(self) -> cc.Variable:
        """Returns the C initialiser for the parameter

        Example:
        ```
        uint32_t my_parameter = 0;
        ```
        """

        assert isinstance(self._resolved_type, RegularCDataType)
        return self._resolved_type.to_c_initialiser(self._name, self.default)

    def to_object_initialiser(self) -> cc.Variable:
        """Returns the odin C initialiser for the parameter"""

        # permission_flags = self._access_configuration.get_permission_flags()

        assert isinstance(self._resolved_type, RegularCDataType)

        formatted_extension = None
        if self.extensions:
            next = None
            for extension in self.extensions:
                formatted_extension = extension.as_literal(self, next)
                next = formatted_extension

        parameter = ODIN_ParameterModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self.absolute_variable_reference,
            name=self._name,
            description=self.resolved_description,
            extensions=formatted_extension,
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

    def to_variable_initialiser(self) -> None:
        """No need to initialise a ram storage entry because the parameter is referenced"""
        return None

    def to_object_initialiser(self) -> cc.Variable:
        """Returns the odin C initialiser for the parameter"""

        assert isinstance(self._resolved_type, RegularCDataType)
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
    _resolved_type: DataType = PrivateAttr()
    default: Any | None = Field(
        description="Default value of the parameter", default=None
    )
    elements: int = Field(description="Number of elements in the array")

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_variable_initialiser(self) -> cc.Variable:
        """Returns the C initialiser for the parameter

        Example:
        ```
        uint32_t my_parameter = 0;
        ```
        """

        assert isinstance(self._resolved_type, RegularCDataType)
        return self._resolved_type.to_c_array_initialiser(
            self._name, self.default if self.default else [], [self.elements]
        )

    def to_object_initialiser(self) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self.absolute_variable_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.elements,
        )
        return parameter.variable


class VectorParameterModel(BaseParameterModel):
    type: str = Field(description="Primitive type of the element in the array")
    _resolved_type: DataType = PrivateAttr()
    default: List[Any] | None = Field(
        description="Default value of the parameter", default=None
    )
    max_elements: int = Field(description="Number of elements in the array")

    def post_load_resolve(
        self, parent: BaseParameterModel | None, name: str, type_registry: TypeRegistry
    ):
        super().post_load_resolve(parent, name, type_registry)
        self._resolved_type = type_registry.get_type(self.type)

    def one_line_summary(self, level=0):
        return f"{level * '  '}{self._name} (0x{self.global_id:08X}): {self.type} - {self._resolved_type.size} bytes"

    def to_variable_type(
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

    def to_variable_initialiser(self) -> cc.Variable:
        data = self._resolved_type.to_c_array_initialiser(
            self._name, self.default, [self.max_elements]
        )

        return cc.Variable(
            name=self._name,
            primitive="UNKNOWN PRIMITIVE",
            value={"data": data.value, "num_elements": len(self.default)},  # type: ignore
        )

    def to_object_initialiser(self) -> cc.Variable:
        assert isinstance(self._resolved_type, RegularCDataType)

        parameter = ODIN_ArrayModel(
            type=self._resolved_type,
            access_group=self.access_control.collapse().to_c_definition(),
            local_index=self.local_id,
            global_index=self.global_id,
            data=self.absolute_variable_reference,
            name=self._name,
            description=self.resolved_description,
            num_elements=self.max_elements,
            fixed_size=False,
        )
        return parameter.variable


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

    # Reference to the variable which stores the group
    _absolute_group_reference: str | None = PrivateAttr(default=None)

    @property
    def absolute_group_reference(self) -> str:
        assert self._absolute_group_reference is not None, "Group reference is not set"
        return self._absolute_group_reference

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
        self.build_global_id_map()

    def one_line_summary(self, level=0):
        val = f"{level * '  '}{self._name} (0x{self.global_id:08X})"
        for child in self.children.values():
            val += f"\n{child.one_line_summary(level + 1)}"
        return val

    def to_object_type(
        self,
    ) -> cc.Struct:
        if isinstance(self, RootParameterModel):
            assert self._c_types is not None, "C types are not set"
            struct = StructVariable(name=self._c_types.objects_type, typedef=True)

        else:
            struct = StructVariable(var_name=self._name, typedef=False)

        # Create the data structures for groups
        for child in self.children.values():
            if isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_object_type())

            elif (
                isinstance(child, ParameterModel)
                or isinstance(child, ReferenceParameterModel)
                or isinstance(child, VectorParameterModel)
                or isinstance(child, ArrayParameterModel)
            ):
                struct.add_variable(child.to_object_initialiser())

            else:
                raise ValueError("Unknown type")

        return struct

    def to_variable_type(
        self,
    ) -> cc.Struct:
        if isinstance(self, RootParameterModel):
            assert self._c_types is not None, "C types are not set"
            struct = StructVariable(name=self._c_types.variables_type, typedef=True)
        else:
            struct = StructVariable(var_name=self._name, typedef=False)

        for child in self.children.values():
            if isinstance(child, ParameterGroupModel):
                struct.add_struct(child.to_variable_type())

            elif isinstance(child, VectorParameterModel):
                child.to_variable_initialiser()
                struct.add_struct(child.to_variable_type())

            elif isinstance(child, ParameterModel) or isinstance(
                child, ArrayParameterModel
            ):
                variable = child.to_variable_initialiser()
                if variable:
                    struct.add_variable(variable)

            elif isinstance(child, ReferenceParameterModel):
                pass

            else:
                raise ValueError("Unknown type")

        return struct

    def to_variable_initialiser(self) -> cc.Variable:
        if isinstance(self, RootParameterModel):
            assert self._c_types is not None, "C types are not set"
            name = self._c_types.variables_name
            type = self._c_types.variables_type
        else:
            name = self._name
            type = "UNKNOWN PRIMITIVE"

        values = {}
        for child in self.children.values():
            initialiser = child.to_variable_initialiser()

            if initialiser:
                values[initialiser.name] = initialiser.value

        return cc.Variable(name=name, primitive=type, value=values)  # type: ignore

    def to_object_initialiser(self) -> cc.Variable:
        if isinstance(self, RootParameterModel):
            assert self._c_types is not None, "C types are not set"
            name = self._c_types.objects_name
            type = self._c_types.objects_type
        else:
            name = self._name
            type = "UNKNOWN PRIMITIVE"

        return cc.Variable(
            name=name,
            primitive=type,
            value={
                parameter_name: parameter.to_object_initialiser().value
                for parameter_name, parameter in self.children.items()  # type: ignore
            },
        )

    def to_group_initialiser(self) -> List[cc.Variable]:
        variables = []

        # Create the data structures for this group
        parameters_references = []
        for parameter in self.children.values():
            if isinstance(parameter, BaseParameterGroupModel):
                parameters_references.append(parameter.absolute_group_reference)
            else:
                parameters_references.append(parameter.absolute_object_reference)

        variables.append(
            ODIN_ParameterGroupModel(
                param_name=self.absolute_group_reference,
                name=self._name,
                description=self.resolved_description,
                global_id=self.global_id,
                id_space_shift=self.id_space_shift,
                parameters_references=parameters_references,
            ).variable
        )

        # Create the data structures for the children
        for parameter in self.children.values():
            if isinstance(parameter, ParameterGroupModel):
                variables.extend(parameter.to_group_initialiser())

        return variables

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

    @property
    def child_map(self) -> Dict[str, BaseParameterModel]:
        child_map = {}
        for child in self.children.values():
            child_map[child._name] = child

        return child_map

    def find_parameter_by_object_name(self, name: str) -> BaseParameterModel | None:
        # Based name
        split_name = name.split(".")
        base_name = split_name[0]

        child_map = self.child_map

        if base_name not in child_map:
            return None

        parameter = child_map[base_name]
        
        if isinstance(parameter, BaseParameterGroupModel):
            assert len(split_name) > 1, "Group name is not set"
            return parameter.find_parameter_by_object_name(".".join(split_name[1:]))
            
        return parameter



class ParameterGroupModel(BaseParameterGroupModel):
    pass


class RootParameterModel(BaseParameterGroupModel):
    local_id: int = 0

    _c_types: C_Names | None = PrivateAttr(default=None)

    def dump_json(self):
        return self.model_dump_json(indent=2)

    def to_access_control_header(self) -> List[str]:
        # todo possible move this into acces contol info?
        assert self.access_control is not None, "Access control info is not set"
        groups = self.access_control.get_access_group_ids()

        defines = []
        for id, name in groups.items():
            defines.append(f"#define ODIN_ACCESS_{name.upper()} ODIN_ACCESS_GROUP_{id}")

        return defines

    def initialise_types(self, types: C_Names):  # type: ignore
        self._c_types = types
        self._absolute_variable_reference = types.variables_name
        self._absolute_object_reference = types.objects_name
        self._absolute_group_reference = types.groups_name

        for child in self.children.values():
            child.initialise_types()
