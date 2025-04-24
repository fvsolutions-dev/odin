import asyncio
import struct
from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar
from typing import Generator


T = TypeVar("T")


class TemplateInterface:
    pass


class GenericModel(ABC):
    @staticmethod
    @abstractmethod
    def encode(value) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def decode(data: bytes) -> Any:
        pass


class ODINBaseEntry:
    interface: TemplateInterface

    def register_interface(self, interface: TemplateInterface):
        self.interface = interface


class ODINEntry(Generic[T], ODINBaseEntry):
    def __init__(self, id: int, cls: Type[GenericModel]):
        self.id = id
        self.type_class = cls

    async def read_with_timeout(self, timeout: float = 0.2) -> T | None:
        try:
            return self.type_class.decode(await asyncio.wait_for(self.interface.get_single(self.id), timeout))  # type: ignore
        except TimeoutError:
            return None

    async def read(self) -> T:
        return self.type_class.decode(await self.interface.get_single(self.id))  # type: ignore

    async def set(self, value: T):
        await self.interface.set_request({self.id: self.type_class.encode(value)})  # type: ignore


class OdinF32(GenericModel):
    BASE_TYPE = float

    @staticmethod
    def encode(value: float) -> bytes:
        return struct.pack("f", value)

    @staticmethod
    def decode(data: bytes) -> float:
        return struct.unpack("f", data)[0]


class OdinI32(GenericModel):
    BASE_TYPE = int

    @staticmethod
    def encode(value: int) -> bytes:
        return struct.pack("i", value)

    @staticmethod
    def decode(data: bytes) -> int:
        return struct.unpack("i", data)[0]


class OdinBool(GenericModel):
    BASE_TYPE = bool

    @staticmethod
    def encode(value: bool) -> bytes:
        return struct.pack("?", value)

    @staticmethod
    def decode(data: bytes) -> bool:
        return struct.unpack("?", data)[0]


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
