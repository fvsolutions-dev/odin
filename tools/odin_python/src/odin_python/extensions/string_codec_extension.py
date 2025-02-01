from typing import Literal

from pydantic import BaseModel, Field
from .common import BaseExtension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parameter.parameter import BaseParameterModel


class StringCodecExtension(BaseExtension): ...


class ReferenceStringCodecExtension(StringCodecExtension):
    type: Literal["string_codec_reference"]
    reference: str = Field(description="Reference to another odin parameter")
