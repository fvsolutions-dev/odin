from .validation import ValidationParameterExtensionModel
from .reference import ReferenceParameterExtensionModel

EXENSIONS = ValidationParameterExtensionModel | ReferenceParameterExtensionModel

__all__ = ["ValidationParameterExtensionModel", "ReferenceParameterExtensionModel", "EXENSIONS"]
