from typing import List
from pydantic import BaseModel, Field, PrivateAttr
from enum import Enum
from typing import Dict
import csnake as cc


class AccessMode(Enum):
    """Access mode for a parameter."""

    NO_ACCESS = "no_access"
    READ_ONLY = "read"
    WRITE_ONLY = "write"
    READ_WRITE = "read_write"

    @classmethod
    def from_str(cls, value: str) -> "AccessMode":
        if value.upper() in ["R", "READ"]:
            return cls.READ_ONLY
        elif value.upper() in ["W", "WRITE"]:
            return cls.WRITE_ONLY
        elif value.upper() in ["RW", "READ_WRITE", "READWRITE"]:
            return cls.READ_WRITE
        elif value.upper() in ["NA", "NO_ACCESS"]:
            return cls.NO_ACCESS

        raise ValueError(f"Invalid access option: {value}")


class AccessFlag(Enum):
    READ = "READ"
    WRITE = "WRITE"

    def macro_name(self, name: str) -> str:
        return f"ODIN_ACCESS_{name.upper()}_{self.value.upper()}"

    def to_shift_reference(self) -> str:
        if self == AccessFlag.READ:
            return "ODIN_READ_ACCESS"
        if self == AccessFlag.WRITE:
            return "ODIN_WRITE_ACCESS"

        raise ValueError(f"Invalid access flag: {self}")


class AccessConfigurationModel(BaseModel):
    _name: str = PrivateAttr()
    default: str | None = Field(default=None)
    force: str | None = Field(default=None)
    log: str | None = Field(default=None)

    read_allowed: bool = False
    write_allowed: bool = False

    def apply_default(self):
        if self.default is not None:
            self.apply_permissions(AccessMode.from_str(self.default))

    def apply_permissions(self, options: AccessMode):
        if options == AccessMode.READ_ONLY:
            self.read_allowed = True
            self.write_allowed = False
        elif options == AccessMode.WRITE_ONLY:
            self.write_allowed = True
            self.read_allowed = False
        elif options == AccessMode.READ_WRITE:
            self.read_allowed = True
            self.write_allowed = True
        elif options == AccessMode.NO_ACCESS:
            self.read_allowed = False
            self.write_allowed = False
        else:
            raise ValueError(f"Invalid access option: {options}")

    @property
    def active_flags(self) -> List[AccessFlag]:
        flags = []
        if self.read_allowed:
            flags.append(AccessFlag.READ)
        if self.write_allowed:
            flags.append(AccessFlag.WRITE)
        return flags

    def get_permission_flags(self) -> List[str]:
        if self.force is not None:
            self.apply_permissions(AccessMode.from_str(self.force))

        return [flag.macro_name(self._name) for flag in self.active_flags]


AccessConfigurationType = Dict[str, AccessConfigurationModel | None]
AccessConfigurationTypeFactory = dict

# Create options type
AccessOptionsType = Dict[str, str]
AccessOptionsTypeFactory = dict


class AccessConfigurations(BaseModel):
    configurations: AccessConfigurationType

    def create_code(self, cw: cc.CodeWriter):
        for i, (group_name, access_group) in enumerate(self.configurations.items()):
            BASE = f"ODIN_ACCESS_{group_name.upper()}"
            cw.add_line(f"#define {BASE} (1<<{i*2})")

            for access_type in AccessFlag:
                cw.add_line(
                    f"#define {access_type.macro_name(group_name)} ({BASE} << {access_type.to_shift_reference()})"
                )

            cw.add_line("")

    def apply_defaults(self):
        for k, v in self.configurations.items():
            assert v is not None, "Configuration should not be None"
            v.apply_default()

    @classmethod
    def inherit(
        cls,
        parent: "AccessConfigurationType|AccessConfigurations",
        config: AccessOptionsType | None,
    ) -> "AccessConfigurations":
        if not isinstance(parent, AccessConfigurations):
            parent = cls(configurations=parent)
            parent.apply_defaults()

        # Create a copy
        parent = parent.model_copy()

        if config is not None:
            for k, v in config.items():
                if k not in parent.configurations:
                    raise ValueError(f"Acces group {k} not does not exist")
                cfg = parent.configurations[k]

                assert cfg is not None, "Configuration should not be None"

                cfg.apply_permissions(AccessMode.from_str(v))

        return parent

    def get_permission_flags(self) -> List[str]:
        flags = []
        for k, v in self.configurations.items():
            if v is not None:
                flags.extend(v.get_permission_flags())
        return flags
