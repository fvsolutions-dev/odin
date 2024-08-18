from .validation import ValidationParameterExtensionModel
from .reference import ReferenceParameterExtensionModel
from .custom import CustomParameterExtensionModel

EXENSIONS = (
    ValidationParameterExtensionModel
    | ReferenceParameterExtensionModel
    | CustomParameterExtensionModel
)

__all__ = [
    "ValidationParameterExtensionModel",
    "ReferenceParameterExtensionModel",
    "EXENSIONS",
    "CustomParameterExtensionModel",
]
