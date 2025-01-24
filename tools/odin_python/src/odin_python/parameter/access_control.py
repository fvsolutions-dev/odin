from enum import Enum
from typing import Dict, List, TYPE_CHECKING, Set


from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    RootModel,
    field_validator,
    model_validator,
)


if TYPE_CHECKING:
    from odin_python.parameter.parameter import BaseParameterModel, RootParameterModel

MAX_ACCESS_GROUPS = 6

# class AccesControlCollection(RootModel[]


class AccesContolEnum(Enum):
    """Access control enum, list all the possible access control items"""

    READ = "read"
    WRITE = "write"
    LOG_WRITE = "log_write"
    LOG_READ = "log_read"

    @staticmethod
    def from_compact_representation(string: str) -> Set["AccesContolEnum"]:
        items = set()
        if "R" in string:
            items.add(AccesContolEnum.READ)
        if "W" in string:
            items.add(AccesContolEnum.WRITE)
        return items

    @classmethod
    def from_string(cls, input: str) -> "AccesContolEnum":
        if input.upper() in AccesContolEnum.__members__:
            return AccesContolEnum[input.upper()]
        else:
            raise ValueError(f"Unknown access control item {input}")

    @staticmethod
    def parse(
        input: "str | Set[str] | Set[AccesContolEnum]",
    ) -> "Set[AccesContolEnum]":
        if isinstance(input, str):
            return AccesContolEnum.from_compact_representation(input)

        elif isinstance(input, set):
            items = set()
            for item in input:
                if isinstance(item, str):
                    items.add(AccesContolEnum.from_string(item))
                else:
                    items.add(item)
            return items


class AccesControlEntry(BaseModel):
    override: Set[str] | Set[AccesContolEnum] | str | None = Field(
        default=None,
        description="Override the default access control for the given group, if not specified it will not override",
    )

    default: Set[str] | Set[AccesContolEnum] | str = Field(
        default_factory=set, description="Default access control for the given group"
    )

    # Field validator that converts to set
    @model_validator(mode="after")  # type: ignore
    def convert_fields(cls, model: "AccesControlEntry") -> "AccesControlEntry":
        model.default = AccesContolEnum.parse(model.default)
        if model.override is not None:
            model.override = AccesContolEnum.parse(model.override)
            # Add to default if not already present
            model.default = model.default.union(model.override)
            
        return model

    @classmethod
    def empty(cls):
        return cls()

    def merge(self, other: "AccesControlEntry") -> "AccesControlEntry":
        if self.override is not None and other.override is None:
            return AccesControlEntry(override=self.override, default=self.override)

        elif other.override is not None:
            return AccesControlEntry(override=other.override, default=other.override)

        else:
            return AccesControlEntry(
                override=self.override, default=self.default.union(other.default)
            )  # type: ignore

    @classmethod
    def normalize(
        cls, input: "str | Set[str]|AccesControlEntry"
    ) -> "AccesControlEntry":
        if isinstance(input, AccesControlEntry):
            return input

        return cls(default=AccesContolEnum.parse(input))

    def to_statement(self, group_name: str) -> str | None:
        permissions = []

        for permission in self.default:
            permissions.append(f"ODIN_ACCESS_{permission.name.upper()}")

        if len(permissions) == 0:
            return None

        return f"(ODIN_ACCESS_{group_name.upper()} & ({' | '.join(permissions)}))"


class AccesControlCollection(RootModel[Dict[str, AccesControlEntry | Set[str] | str]]):
    # Reference to parent parameter model
    _parent: "BaseParameterModel | None" = PrivateAttr(default=None)

    pass

    @classmethod
    def empty(cls):
        return cls({})

    def to_defines(self) -> str:
        statements = []
        for group_name, entry in self.root.items():
            statement = entry.to_statement(group_name)
            if statement is not None:
                statements.append(statement)

        if len(statements) == 0:
            return "0"

        return " | ".join(statements)

    def get_defs(self) -> str:
        acl_chain = self.recursive_get_build_permission_chain(self)

        last = None
        for item in acl_chain:
            if last is None:
                last = item
                continue
            last = last.merge(item)

        return last.to_defines()

    @staticmethod
    def recursive_get_build_permission_chain(
        current: "AccesControlCollection",
    ) -> "List[AccesControlCollection]":
        from odin_python.parameter.parameter import RootParameterModel

        parameter = current._parent

        acls: List[AccesControlCollection]

        if not isinstance(parameter, RootParameterModel):
            assert parameter is not None, "No parameter found for this entry"
            assert parameter._parent is not None, "No parent found for the parameter"

            acls = AccesControlCollection.recursive_get_build_permission_chain(
                parameter._parent.access_control
            )

        else:
            acls = []

        acls.append(current)
        return acls

    _access_groups: Dict[int, str] | None = PrivateAttr(default=None)

    def validate_group(self):
        if self._access_groups is None:
            self._access_groups = {}

            for id, (group_name, entry) in enumerate(self.root.items()):
                self._access_groups[id] = group_name

                if id >= MAX_ACCESS_GROUPS:
                    raise ValueError(
                        f"Only {MAX_ACCESS_GROUPS} access groups are allowed"
                    )

        return self._access_groups

    def merge(self, other: "AccesControlCollection") -> "AccesControlCollection":
        # Create master set of both access control groups

        items: Dict[str, AccesControlEntry] = {}

        for name, item in self.root.items():
            if not isinstance(item, AccesControlEntry):
                item = AccesControlEntry.normalize(item)

            items[name] = item

        for name, item in other.root.items():
            if not isinstance(item, AccesControlEntry):
                item = AccesControlEntry.normalize(item)

            if name not in items:
                items[name] = item
            else:
                items[name] = items[name].merge(item)

        return AccesControlCollection(root=items)  # type: ignore

    # def to_access_control_header(self) -> str:
    #     cw = cc.CodeWriter()
    #     for group_name, entry in self.access_control.items():
    #         if entry.override:
    #             cw.add_line(f"#define {group_name.upper()}_ACCESS_CONTROL {entry.override}")
    #         else:
    #             cw.add_line(f"#define {group_name.upper()}_ACCESS_CONTROL {entry.default}")
    #     return str(cw)
