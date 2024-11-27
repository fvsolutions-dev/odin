from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, PrivateAttr
import csnake as cc
from typing import Dict
from .standard_types import CFormatEnum, CustomCTypesEnum


class GenericDataType(BaseModel, ABC):
    """Base class for all data types

    A type represents a data type that can be used in the system.
    """

    _typename: str = PrivateAttr()  # Name of the type

    @abstractmethod
    def to_c_typedef(self) -> cc.Struct | cc.Enum: ...

    """
    Convert the type to a C typedef, used to define the type in C code
    
    Returns:
        cc.Struct | cc.Enum: The C typedef
    """

    @abstractmethod
    def to_c_initialiser(
        self, types: Dict[str, Any], name: str, default: Dict[str, Any] | None
    ) -> cc.Variable: ...

    """
    Convert the type to a C initialiser, used to initialise the type in C code
    
    Args:
        types (Dict[str, Any]): The types defined in the system
        name (str): The name of the variable
        default (Dict[str, Any] | None): The default value of the variable
        
    Returns:
        cc.Variable: The C initialiser
    """

    @abstractmethod
    def to_c_array_initaliser(
        self,
        types: Dict[str, Any],
        name: str,
        default: Dict[str, Any] | None,
        lenght: int,
    ) -> cc.Variable: ...

    """Convert the type to a C array initialiser, used to initialise an array of the type in C code
    
    Args:
        types (Dict[str, Any]): The types defined in the system
        name (str): The name of the variable
        default (Dict[str, Any] | None): The default value of the variable
        lenght (int): The lenght of the array
        
    Returns:
        cc.Variable: The C array initialiser
    """

    @abstractmethod
    def to_c_value(self, types: Dict[str, Any], value: Any): ...
    """Convert the type to a C value, used to convert a value to C code
    
    Args:
        types (Dict[str, Any]): The types defined in the system
        value (Any): The value to convert
    """

    @property
    @abstractmethod
    def default_format(self) -> "CFormatEnum": ...
    """The default format of the type"""
    
    @property
    @abstractmethod
    def element_type(self) -> CustomCTypesEnum: ...
    """The element type of the type"""
    