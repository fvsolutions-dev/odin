from typing import Literal

from csnake import FormattedLiteral
from pydantic import BaseModel, Field


class IOExtension(BaseModel):
    pass

class ReferenceIOExtension(IOExtension):
    type: Literal["io_reference"]
    reference: str = Field(description="Reference to another odin parameter")
    offset: float = Field(
        default=0.0, description="Offset to add to the referenced value"
    )
    scale: float = Field(
        default=1.0, description="Scale to multiply the referenced value by"
    )

