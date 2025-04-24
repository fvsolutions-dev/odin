import asyncio
import struct
from abc import ABC, abstractmethod
from typing import Any, Generator, Generic, Self, Type, TypeVar

T = TypeVar("T")


class TemplateInterface:
    pass


class GenericModel(ABC):
    @abstractmethod
    def encode_to_bytes(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def decode_from_bytes(cls, data: bytes) -> Self:
        pass


class ODINEntry(Generic[T]):
    interface: TemplateInterface

    def __init__(self, id: int, cls: Type[GenericModel], interface: TemplateInterface):
        self.id = id
        self.type_class = cls
        self.interface = interface

    async def read_with_timeout(self, timeout: float = 0.2) -> T | None:
        try:
            return self.type_class.encode_to_bytes(await asyncio.wait_for(self.interface.get_single(self.id), timeout))  # type: ignore
        except TimeoutError:
            return None

    async def read(self) -> T:
        return self.type_class.decode_from_bytes(await self.interface.get_single(self.id))  # type: ignore

    async def set(self, value: T):
        await self.interface.set_request({self.id: self.type_class.encode(value)})  # type: ignore


class BaseRootModel:
    _children: dict[str, "ODINEntry|BaseRootModel"]

    def __init__(self, interface: TemplateInterface):
        self.interface = interface

    async def read_all(self) -> dict[str, Any]:
        data = {}
        for name, odin_var in self._children.items():
            if isinstance(odin_var, BaseRootModel):
                data[name] = await odin_var.read_all()
            else:
                data[name] = await odin_var.read()

        return data