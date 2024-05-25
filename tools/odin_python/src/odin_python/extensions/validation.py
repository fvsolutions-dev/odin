from typing import Literal

from csnake import FormattedLiteral
from pydantic import BaseModel


class ValidationParameterExtensionModel(BaseModel):
    type: Literal["limit_value"]
    min: float | None = None
    max: float | None = None

    def as_literal(self) -> FormattedLiteral:
        if self.min is None:
            self.min = -float("inf")
        if self.max is None:
            self.max = float("inf")

        value = (
            f"(ODIN_extension_t[]){{ {{ .ops = &range_validator_extension, .data = &(range_parameter_t){{ .max = {self.max}, .min = {self.min} }} }} }}"
        )

        return FormattedLiteral(
            value,  # type: ignore
            string_formatter=str,
        )
    
    def required_references(self) -> None:
        return None

