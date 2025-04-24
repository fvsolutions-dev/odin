import asyncio
import struct
from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar
from typing import Generator



class BaseRootModel:
    def __init__(self, interface: TemplateInterface):
        self.interface = interface

        # Register interface onto self
        for name, _ in self._get_odin_variables():
            odin_var: ODINEntry = getattr(self, name)
            odin_var.register_interface(self.interface)

    @classmethod
    def _get_odin_variables(cls) -> Generator[tuple[str, ODINEntry], None, None]:
        for base in cls.__mro__:
            for name, attr in base.__dict__.items():
                if isinstance(attr, ODINBaseEntry):
                    yield name, attr  # type: ignore
