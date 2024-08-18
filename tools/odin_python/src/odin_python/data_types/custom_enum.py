from typing import Any, Dict, List, Literal

import csnake as cc

from .generic import GenericDataType

from .standard_types import CFormatEnum, CustomCTypesEnum


class EnumeratorDataType(GenericDataType):
    type: Literal["enumerator"]
    values: Dict[str, int]
    default: str | int | None = None

    @property
    def prefix(self):
        return f"{self._typename.upper()}_"

    def apply_prefix(self, value):
        return f"{self.prefix}{value}"

    def to_c_typedef(self):
        enum = cc.Enum(
            name=self._typename,
            typedef=True,
        )

        for k, v in self.values.items():
            enum.add_value(name=self.apply_prefix(k.upper()), value=v)  # type: ignore

        return enum

    def to_c_array_initaliser(
        self,
        types: Dict[str, Any],
        name: str,
        default: List[str | int] | str | int | None,
        length: int,
    ) -> cc.Variable:
        if default is None or isinstance(default, (str, int)):
            if default is None:
                default = self.default

            assert default is not None, f"Default value not set for {name}"

            _default = [self.to_c_value(types, default)] * length
        else:
            if isinstance(default, (str, int)):
                _default = [self.to_c_value(types, default)] * length
            assert (
                len(default) == length
            ), f"Length of {name} only has {len(default)} default values, but {length} are required"
            _default = [self.to_c_value(types, v) for v in default]

        assert _default is not None, f"Default value not set for {name}"

        return cc.Variable(
            name=name,
            primitive=self._typename,
            value=_default,  # type: ignore
            array=[length],
        )

    def to_c_initialiser(
        self,
        types: Dict[str, Any],
        name: str,
        default: str | int | None,
    ) -> cc.Variable:
        if default is None:
            default = self.default

        assert default is not None, f"Default value not set for {name}"

        return cc.Variable(
            name=name,
            primitive=self._typename,
            value=self.to_c_value(types, default),  # type: ignore
        )

    def to_c_value(self, types: Dict[str, Any], value: str | int) -> cc.TextModifier:
        for k, v in self.values.items():
            if k == value or v == value:
                return cc.TextModifier(self.apply_prefix(k.upper()))  # type: ignore

        raise ValueError(f"Value {value} not found in {self._typename}")

    @property
    def default_format(self) -> "CFormatEnum":
        return CFormatEnum.NUMBER

    @property
    def element_type(self) -> CustomCTypesEnum:
        return CustomCTypesEnum.ENUMERATOR
