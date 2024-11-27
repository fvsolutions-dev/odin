from typing import Dict


class BaseType:
    pass


class TypeRegistry:
    def __init__(self):
        self._types: Dict[str, BaseType] = {}

    def register(self, type: BaseType):
        """Register a new type"""

        if type.__name__ in self._types:
            raise ValueError(f"Type {type.__name__} already registered")

        if not issubclass(type, BaseType):
            raise ValueError(f"Type {type.__name__} is not a subclass of BaseType")

        self._types[type.__name__] = type

    def get_type(self, name: str):
        """Get a type by name"""

        if name not in self._types:
            raise ValueError(f"Type {name} not found")

        return self._types[name]
