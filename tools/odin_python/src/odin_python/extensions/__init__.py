from .io_extension import ReferenceIOExtension
from .validation_extension import LimitValidationExtension
from .string_codec_extension import ReferenceStringCodecExtension
from typing import Annotated, Union
from pydantic import Discriminator

Extensions = Annotated[
    Union[
        ReferenceIOExtension,
        LimitValidationExtension,
        ReferenceStringCodecExtension,
    ],
    Discriminator("type"),
]
