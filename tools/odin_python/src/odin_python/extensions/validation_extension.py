from typing import Literal

from pydantic import BaseModel, Field


class ValidationExtension(BaseModel): ...


class LimitValidationExtension(ValidationExtension):
    type: Literal["validation_limit_value"]
    min: float | None = Field(
        default=None, title="Minimum value, if not set, no minimum value is enforced"
    )
    max: float | None = Field(
        default=None,
        title="Maximum allowed value, if not set, no maximum value is enforced",
    )

    # def as_literal(self) -> FormattedLiteral:
    #     if self.min is None:
    #         self.min = -float("inf")
    #     if self.max is None:
    #         self.max = float("inf")

    #     value = f"(ODIN_extension_t[]){{ {{ .ops = &range_validator_extension, .data = &(range_parameter_t){{ .max = {self.max}, .min = {self.min} }} }} }}"

    #     return FormattedLiteral(
    #         value,  # type: ignore
    #         string_formatter=str,
    #     )

    # def required_references(self) -> None:
    #     return None
