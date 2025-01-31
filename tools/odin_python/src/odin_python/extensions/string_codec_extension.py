from typing import Literal

from pydantic import BaseModel, Field


class StringCodecExtension(BaseModel):
    ...
    
class ReferenceStringCodecExtension(StringCodecExtension):
    type: Literal["string_codec_reference"]
    reference: str = Field(description="Reference to another odin parameter")
