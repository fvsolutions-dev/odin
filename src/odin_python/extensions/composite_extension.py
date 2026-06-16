from typing import Literal

from pydantic import Field

from .common import BaseExtension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parameter.parameter import BaseParameterModel


class CompositeExtension(BaseExtension):
    """Attaches an ODIN_EXTENSION_TYPE_COMPOSITE extension to a CUSTOM-typed
    parameter. `descriptor_symbol` is the generated per-type
    ODIN_type_descriptor_t emitted once before the OD (shared by every parameter
    of that type). ops is NULL — the descriptor lives in `.data`."""

    type: Literal["composite"]
    descriptor_symbol: str = Field(description="C symbol of the type descriptor")

    def as_literal(self, parameter: "BaseParameterModel", next: str | None) -> str:
        del parameter  # the descriptor is type-keyed, not parameter-keyed
        next_ref = next if next else "NULL"
        return (
            f"(ODIN_extension_t[]){{ {{\n"
            f"\t\t\t.type=ODIN_EXTENSION_TYPE_COMPOSITE,\n"
            f"\t\t\t.ops =  NULL,\n"
            f"\t\t\t.data = (void*)&{self.descriptor_symbol},\n"
            f"\t\t\t.next = {next_ref} }} }}"
        )
