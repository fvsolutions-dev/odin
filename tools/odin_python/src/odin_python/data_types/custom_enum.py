from typing import Dict, List, Literal

import csnake as cc

from .generic import GenericDataType


class EnumeratorDataType(GenericDataType):
    type: Literal["enumerator"]
    values: Dict[str, int]

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

    def to_c_object(
        self,
        name: str,
        default: str | int | None,
        length: int | None = None,
    ) -> cc.Variable:
        assert default is not None, f"Default value not set for {name}"

        if isinstance(default, List):
            default = [self.to_c_value(v) for v in default]
        else:
            default = self.to_c_value(default)

        return cc.Variable(
            name=name,
            primitive=self._typename,
            value=default,  # type: ignore
            array=[length] if length is not None else None,
        )

    def to_c_value(self, value: str | int) -> cc.TextModifier:
        for k, v in self.values.items():
            if k == value or v == value:
                return cc.TextModifier(self.apply_prefix(k.upper()))  # type: ignore

        raise ValueError(f"Value {value} not found in {self._typename}")
