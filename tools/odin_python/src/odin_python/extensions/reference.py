from typing import Literal

from csnake import FormattedLiteral
from pydantic import BaseModel


class ReferenceParameterExtensionModel(BaseModel):
    type: Literal["reference"]
    reference: str
    offset: float = 0.0
    scale: float = 1.0

    def as_literal(self) -> FormattedLiteral:
        value = (
            f"(ODIN_extension_t[]){{ {{ .ops = &parameter_mapping_extension, .data = &(mapped_parameter_t){{ .reference = &{self.reference}, .offset = {self.offset}, .scale = {self.scale} }} }} }}"
        )

        return FormattedLiteral(
            value,  # type: ignore
            string_formatter=str,
        )

    def required_references(self) -> None:
        return None

