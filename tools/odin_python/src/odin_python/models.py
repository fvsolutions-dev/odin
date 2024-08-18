import struct
from typing import Dict, List, Union

import csnake as cc
from csnake import CodeWriter, FormattedLiteral
from pydantic import BaseModel, Field, model_validator
from pydantic_yaml import parse_yaml_file_as
from strenum import StrEnum

from .extensions import (
    EXENSIONS,
    ReferenceParameterExtensionModel,
)
from .types import CFormatEnum, CTypeEnum
from .utils.csnake_custom import StructVariable
from .utils.string import escape_string

ODIN_STORE_TYPE = "ODIN_store_t"
ODIN_PARAMETER_TYPE = "ODIN_parameter_t"
ODIN_GROUP_TYPE = "ODIN_parameter_group_t"
ODIN_ENCODING_TYPE_PREFIX = "ODIN_ENCODING_"
ODIN_TYPE_PREFIX = "ODIN_ELEMENT_TYPE_"


class CNames(BaseModel):
    datastore_name: str = "ODIN_store"
    ram_params_name: str = "ODIN_ram"
    params_name: str = "ODIN_params"


class ParameterModel(BaseModel):
    """Stores all the information for a parameter."""

    _group_id: int | None = None
    _variable_names: CNames | None = None

    # _ram_params_name: str | None = None
    # _variable_store_name: str | None = None
    _group_name: str | None = None
    _is_reference: bool = False
    _name: str | None = None

    id: int

    access_permissions: Dict[str, str] = Field(default_factory=dict)
    description: str
    primitive: CTypeEnum
    format: CFormatEnum = Field(
        default=CFormatEnum.AUTO,
        description="The format of the data. If set to 'auto', the format will be determined based on the primitive type.",
    )
    length: int | None = None
    default: Union[
        int, float, str, bool, List[int], List[float], List[str], List[bool]
    ] = 0
    persistent: bool = False
    extension: EXENSIONS | None = None

    @model_validator(mode="after")
    def check_reference(self) -> "ParameterModel":
        if self.extension and isinstance(
            self.extension, ReferenceParameterExtensionModel
        ):
            self._is_reference = True
        return self

    @property
    def qualified_id(self) -> int:
        assert self._group_id is not None
        return (self._group_id << 16) | self.id

    @property
    def variable_reference(self):
        assert self._variable_names
        assert self._name
        assert self._group_name
        return f"{self._variable_names.ram_params_name}.{self._group_name}.{self._name}"

    @property
    def parameter_reference(self):
        assert self._name
        assert self._group_name
        assert self._variable_names
        return f"{self._variable_names.params_name}.{self._group_name}.{self._name}"

    def as_variable(self) -> cc.Variable:
        assert self._name
        return cc.Variable(
            name=self._name,
            primitive=self.primitive,
            array=[self.length] if self.length else None,
        )

    def as_parameter(self, access_opts: "AccessOptionsGenerator") -> Dict:
        assert self._group_id is not None
        id = (self._group_id << 16) | self.id
        data = {
            "index": FormattedLiteral(id, int_formatter=hex),
            "access": access_opts.as_literal(self),
            "format": FormattedLiteral(
                self.format.odin_type_conv(self.primitive, self.length),
                string_formatter=str,
            ),
            "type": FormattedLiteral(
                self.primitive.odin_type_define, string_formatter=str
            ),
            "data": FormattedLiteral(
                f"&{self.variable_reference}", string_formatter=str
            ),
            "size": FormattedLiteral(
                self.primitive.sizeof(self.length), string_formatter=str
            ),
            "name": self._name,
            "description": escape_string(self.description),
        }

        if self.extension:
            data["extension"] = self.extension.as_literal()

        if self._is_reference:
            data["data"] = FormattedLiteral("NULL", string_formatter=str)

        return data

    def as_odin_parameter(self) -> cc.Variable:
        var = cc.Variable(
            name=self._name,
            primitive=ODIN_PARAMETER_TYPE,
        )
        return var

    def as_ram_parameter(self) -> cc.Variable | None:
        if self._is_reference:
            return None

        var = cc.Variable(
            name=self._name,
            primitive=self.primitive,
            array=[self.length] if self.length else None,
            value=self.default,
        )
        return var

    def to_values(self, data: bytes):
        if self.length is not None:
            return data

        if self.primitive == CTypeEnum.UINT8:
            return struct.unpack("B", data)[0]
        if self.primitive == CTypeEnum.INT8:
            return struct.unpack("b", data)[0]
        if self.primitive == CTypeEnum.UINT16:
            return struct.unpack("H", data)[0]
        if self.primitive == CTypeEnum.INT16:
            return struct.unpack("h", data)[0]
        if self.primitive == CTypeEnum.UINT32:
            return struct.unpack("I", data)[0]
        if self.primitive == CTypeEnum.INT32:
            return struct.unpack("i", data)[0]
        if self.primitive == CTypeEnum.UINT64:
            return struct.unpack("Q", data)[0]
        if self.primitive == CTypeEnum.INT64:
            return struct.unpack("q", data)[0]
        if self.primitive == CTypeEnum.FLOAT:
            return struct.unpack("f", data)[0]
        if self.primitive == CTypeEnum.DOUBLE:
            return struct.unpack("d", data)[0]
        if self.primitive == CTypeEnum.BOOL:
            return bool(data[0])


class DeviceGroupModel(BaseModel):
    id: int
    _name: str | None = None
    _variable_names: CNames | None = None

    description: str
    data: Dict[str, ParameterModel]
    access_permissions: Dict[str, str] = Field(default_factory=dict)

    @property
    def c_type(self) -> str:
        assert self._name
        return f"{self._name}_t"

    @property
    def group_reference(self):
        assert self._name
        assert self._variable_names
        return f"{self._variable_names.datastore_name}_{self._name}"

    def as_struct(self) -> cc.Struct:
        assert self._name

        struct = cc.Struct(self.c_type, typedef=True)
        for parameter_name, parameter in self.data.items():
            struct.add_variable(parameter.as_variable())
        return struct

    def as_variable_initialization(self) -> cc.Variable:
        assert self._name

        return cc.Variable(
            name=self._name,
            primitive=self.c_type,
            value={
                parameter_name: parameter.default
                for parameter_name, parameter in self.data.items()
            },
        )

    def as_parameter_group(self, acces_opt: "AccessOptionsGenerator") -> Dict:
        params = {}
        for parameter_name, parameter in self.data.items():
            params[parameter_name] = parameter.as_parameter(acces_opt)
        return params

    def as_reference(self) -> cc.Variable:
        params = []
        for parameter_name, parameter in self.data.items():
            params.append(
                FormattedLiteral(
                    f"&{parameter.parameter_reference}", string_formatter=str
                )
            )

        data = {
            "name": self._name,
            "description": escape_string(self.description),
            "index": FormattedLiteral(self.id, int_formatter=hex),
            "count": len(self.data),
            "parameters": params,
        }

        return cc.Variable(
            name=self.group_reference,
            primitive=ODIN_GROUP_TYPE,
            value=data,
        )


class PermissionDefModel(BaseModel):
    force: str | None = None
    log: str | None = None


class MainModel(BaseModel):
    access_groups: Dict[str, PermissionDefModel] = Field(
        description="Defines the access groups."
    )
    variable_names: CNames = Field(
        description="Defines the names of the variables.", default_factory=CNames
    )

    groups: Dict[str, List[str]] = Field(
        description="Defines the groups and the parameters that belong to them.",
        default_factory=dict,
    )

    datastore: Dict[str, DeviceGroupModel] = Field(
        description="Holds all the parameters."
    )

    @model_validator(mode="after")
    def populate_names(self):
        """Populate the names of the groups and parameters."""
        for group_name, device_group in self.datastore.items():
            device_group._name = group_name
            device_group._variable_names = self.variable_names
            for parameter_name, parameter in device_group.data.items():
                parameter._name = parameter_name
                parameter._group_name = device_group._name
                parameter._group_id = device_group.id
                parameter._variable_names = self.variable_names

                # Add the access permissions to the parameter
                for name, perms in device_group.access_permissions.items():
                    if name not in parameter.access_permissions:
                        parameter.access_permissions[name] = perms
                    else:
                        parameter.access_permissions[name] += perms

        return self

    @property
    def ram_store_type(self) -> str:
        return f"{self.variable_names.ram_params_name}_t"

    @property
    def datastore_type(self) -> str:
        return f"{self.variable_names.params_name}_t"

    def as_variable(self) -> cc.Variable:
        values_dict = {}
        for group_name, device_group in self.datastore.items():
            values_dict[group_name] = {}
            for parameter_name, parameter in device_group.data.items():
                if parameter._is_reference:
                    continue
                values_dict[group_name][parameter_name] = parameter.default

        return cc.Variable(
            name=self.variable_names.ram_params_name,
            primitive=self.ram_store_type,
            value=values_dict,
            comment="Value storage for the ODIN RAM data store.",
        )

    def as_variable_struct(self) -> StructVariable:
        struct = StructVariable(self.ram_store_type, typedef=True)

        # Create the data structures for groups
        for group_name, device_group in self.datastore.items():
            group_struct = StructVariable(var_name=group_name)
            for parameter in device_group.data.values():
                param = parameter.as_ram_parameter()
                if param:
                    group_struct.add_variable(param)
            struct.add_struct(group_struct)

        return struct

    def as_parameter_store(self, acces_opt: "AccessOptionsGenerator") -> cc.Variable:
        groups = {}
        for group_name, device_group in self.datastore.items():
            groups[group_name] = device_group.as_parameter_group(acces_opt)

        var = cc.Variable(
            self.variable_names.params_name, primitive=self.datastore_type, value=groups
        )
        return var

    def as_parameter_store_struct(self) -> StructVariable:
        struct = StructVariable(self.datastore_type, typedef=True)
        for group_name, data_group in self.datastore.items():
            group_struct = StructVariable(var_name=group_name)
            for parameter in data_group.data.values():
                group_struct.add_variable(parameter.as_odin_parameter())
            struct.add_struct(group_struct)
        return struct

    def as_reference(self) -> cc.Variable:
        params = [
            FormattedLiteral(f"&{group.group_reference}", string_formatter=str)
            for group in self.datastore.values()
        ]

        return cc.Variable(
            name=self.variable_names.datastore_name,
            primitive=ODIN_STORE_TYPE,
            value={
                "count": len(self.datastore),
                "groups": params,
            },
        )

    @classmethod
    def from_file(cls, file_path: str) -> "MainModel":
        return parse_yaml_file_as(MainModel, file_path)


class AccessType(StrEnum):
    READ = "READ"
    WRITE = "WRITE"

    def to_flag(self, name: str) -> str:
        return f"ODIN_ACCESS_TYPE_{name.upper()}_{self.value}"

    def to_shift_reference(self) -> str:
        if self == AccessType.READ:
            return "ODIN_READ_ACCESS"
        if self == AccessType.WRITE:
            return "ODIN_WRITE_ACCESS"

    @staticmethod
    def to_access_type_list(opts: str) -> List["AccessType"]:
        # input R or RW or W
        acces = []
        if "R" in opts:
            acces.append(AccessType.READ)
        if "W" in opts:
            acces.append(AccessType.WRITE)
        return acces


class AccessOptions:
    base_shift: int
    name: str
    options: PermissionDefModel

    @property
    def prefix(self) -> str:
        return f"ACCESS_TYPE_{self.name.upper()}"

    def __init__(self, name, options, base_shift):
        self.base_shift = base_shift
        self.name = name
        self.options = options

    def get_flags(self, perms: str) -> List[str]:
        if self.options.force:
            perms = self.options.force

        flags: List[str] = []
        if "R" in perms:
            flags.append(AccessType.READ.to_flag(self.name))
        if "W" in perms:
            flags.append(AccessType.WRITE.to_flag(self.name))
        return flags


class AccessOptionsGenerator:
    access_groups: Dict[str, AccessOptions]

    def __init__(self, config: MainModel):
        self.access_groups = {}
        base_shift = 4
        base_shift_offset = 2

        for access_group_name, access_group_options in config.access_groups.items():
            self.access_groups[access_group_name] = AccessOptions(
                access_group_name, access_group_options, base_shift=base_shift
            )
            base_shift += base_shift_offset

    def as_literal(self, parameter: ParameterModel) -> FormattedLiteral:
        flags: List[AccessOptions] = []
        for group_name, access_group in self.access_groups.items():
            flags += access_group.get_flags(
                parameter.access_permissions.get(group_name, "")
            )

        return FormattedLiteral("|".join(flags), string_formatter=str)

    def add_define_macros(self, cw: CodeWriter):
        for group_name, access_group in self.access_groups.items():
            BASE = f"ODIN_ACCESS_{access_group.name.upper()}"
            cw.add_line(f"#define {BASE} (1<<{access_group.base_shift})")

            for access_type in AccessType:
                cw.add_line(
                    f"#define {access_type.to_flag(access_group.name)} ({BASE} << {access_type.to_shift_reference()})"
                )

            cw.add_line("")

    def add_log_values(self, cw: CodeWriter):
        log_items = []
        for group_name, access_group in self.access_groups.items():
            if not access_group.options.log:
                continue

            for access_type in AccessType.to_access_type_list(access_group.options.log):
                log_items.append(f"{access_type.to_flag(access_group.name)}")

        if len(log_items) == 0:
            log_items.append(0)

        cw.add_line(
            f"uint32_t ODIN_access_log_values = {' | '.join([item for item in log_items])};"
        )
        cw.add_line("")

    def add_log_reference(self, cw: CodeWriter):
        cw.add_line("extern uint32_t ODIN_access_log_values;")
        cw.add_line("")
