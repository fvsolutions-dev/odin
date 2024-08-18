from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, PrivateAttr
import csnake as cc
from typing import Dict

class GenericDataType(BaseModel, ABC):
    """Base class for all data types

    A type represents a data type that can be used in the system.
    """

    _typename: str = PrivateAttr()  # Name of the type

    @abstractmethod
    def to_c_typedef(self): ...

    @abstractmethod
    def to_c_object(self, name: str, default: Dict[str, Any] | None, lenght: int | None = None
    ) -> cc.Variable: ...

    @abstractmethod
    def to_c_value(self, value: Any): ...
