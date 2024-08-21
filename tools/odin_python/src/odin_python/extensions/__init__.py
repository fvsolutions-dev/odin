from .validation import ValidationParameterExtensionModel
from .mapping import MappingParameterExtensionModel
from .custom import CustomParameterExtensionModel

EXENSIONS = (
    ValidationParameterExtensionModel
    | MappingParameterExtensionModel
    | CustomParameterExtensionModel
)

__all__ = [
    "ValidationParameterExtensionModel",
    "MappingParameterExtensionModel",
    "EXENSIONS",
    "CustomParameterExtensionModel",
]
