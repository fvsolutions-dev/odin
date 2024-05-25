from typing import Literal

from csnake import FormattedLiteral
from pydantic import BaseModel


class CustomParameterExtensionModel(BaseModel):
    type: Literal["custom"]
    reference: str

    def as_literal(self) -> FormattedLiteral:
        value = (
            f"(ODIN_extension_t[]){{ {{ .ops = &{self.reference}, .data = NULL }} }}"
        )

        return FormattedLiteral(
            value,  # type: ignore
            string_formatter=str,
        )
    
    def required_references(self) -> str:
        return f"extern ODIN_extension_ops_t {self.reference};"