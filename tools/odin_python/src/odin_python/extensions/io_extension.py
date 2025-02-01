from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from odin_python.generator.model import ODIN_ExtesionModel
from odin_python.generator.odin_defs import ODIN_ExtensionEnum

from .common import BaseExtension

if TYPE_CHECKING:
    from ..parameter.parameter import BaseParameterModel


class IOExtension(BaseExtension):
    pass


class ReferenceIOExtension(IOExtension):
    type: Literal["io_reference"]
    reference: str = Field(description="Reference to another odin parameter")

    def as_literal(self, parameter: "BaseParameterModel", next: str) -> str:

        model = ODIN_ExtesionModel(
            type=ODIN_ExtensionEnum.ODIN_EXTENSION_TYPE_IO,
            ops="ODIN_extension_io_reference_ops",
            parameters=f"(reference_parameters_t){{ .reference = &{self.reference}}}",
            next=next if next else None,
        )

        return model.variable
