from math import e
from typing import Annotated, Dict
from pydantic import BaseModel, PrivateAttr, RootModel
from typing import List, Any
from pydantic import Field
import csnake as cc
from abc import ABC, abstractmethod
import struct


class TypeDefaultModel(BaseModel):
    type: "list[TypeDefaultModel|DataType] | TypeDefaultModel | DataType"
    default: Any | None = Field(description="The default value for the data type", default=None)


class TypeModelDefinition(
    RootModel[
        Annotated[
            "TypeDefaultModel | list[TypeDefaultModel] | list[str] | str ",
            Field(union_mode="left_to_right"),
        ],
    ],
):
    _resolved: "list[TypeDefaultModel|DataType] | TypeDefaultModel | DataType | None" = PrivateAttr(default=None)

    @property
    def resolved(self) -> "list[TypeDefaultModel|DataType] | TypeDefaultModel | DataType":
        """Get the resolved model"""

        assert self._resolved is not None, "Model not resolved"

        return self._resolved

    def resolve(self, registry: "UnresolvedTypeRegistry"):
        """Resolve the model for the data type"""

        if self._resolved is not None:
            return

        if isinstance(self.root, str):
            self._resolved = registry.get_type(self.root)
            return

        if isinstance(self.root, list):
            self._resolved = []

            for item in self.root:
                if isinstance(item, str):
                    self._resolved.append(registry.get_type(item))

                elif isinstance(item, TypeDefaultModel):
                    self._resolved.append(
                        TypeDefaultModel(
                            type=registry.get_type(item.type),
                            default=item.default,
                        )
                    )
                else:
                    raise ValueError(f"Invalid type {item} in model")
            return

        raise ValueError(f"Invalid type {self.root} in model")


class TypeModelDefinitions(
    RootModel[
        Dict[
            str,
            "TypeModelDefinition | TypeModelDefinitions",
        ],
    ],
):
    def resolve(self, registry: "UnresolvedTypeRegistry"):
        """Resolve the model for the data type"""

        for key, value in self.root.items():
            if isinstance(value, TypeModelDefinition):
                value.resolve(registry)
            elif isinstance(value, TypeModelDefinitions):
                value.resolve(registry)
            else:
                raise ValueError(f"Invalid type {value} in model")

    def to_flat_dict(
        self,
        resolve: bool,
        max_depth: int | None = None,
    ) -> Dict[str, TypeModelDefinition]:
        """Convert the model to a flat list of types"""

        result = {}
        for key, value in self.root.items():
            if isinstance(value, TypeModelDefinition):
                result[key] = value
            elif isinstance(value, TypeModelDefinitions):
                if max_depth is not None and max_depth <= 0:
                    raise ValueError(f"Max depth {max_depth} reached for {key}")

                # Decrease the max depth
                if max_depth is not None:
                    sub_results = value.to_flat_dict(resolve=resolve, max_depth=max_depth - 1)
                else:
                    sub_results = value.to_flat_dict(resolve=resolve)

                for sub_key, sub_value in sub_results.items():
                    result[f"{key}_{sub_key}"] = sub_value
            else:
                raise ValueError(f"Invalid type {value} in model")

        if resolve:
            for key, value in result.items():
                result[key] = value._resolved

        return result

    def to_struct_format_string(self) -> str:
        """Convert the model to a struct format string"""
        format_string = ""
        for key, value in self.to_flat_dict(resolve=True).items():
            if isinstance(value, list):
                for i in range(len(value)):
                    _data_type = value[i]
                    assert isinstance(_data_type, (StandardDataType, CustomDataType))
                    format_string += _data_type.to_python_struct()

            elif isinstance(value, StandardDataType):
                format_string += value.to_python_struct()
            else:
                raise ValueError(f"Unknown type {value} for {key}")
        return format_string


class DataType(BaseModel, ABC):
    typename: str
    size: int = Field(description="Size of the data type in bytes")

    @abstractmethod
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable: ...

    @abstractmethod
    def to_c_array_initialiser(self, name: str, defaults: Any, dimensions: List[int]) -> cc.Variable: ...

    @abstractmethod
    def to_python_struct(self) -> str: ...

    def extra_extension(self) -> str | None:
        return None


class StandardDataType(DataType):
    c_typename: str = Field(description="The C typename that corresponds to the data type")
    python_struct_format: str | None = Field(
        description="The python struct format string for the data type", default=None
    )

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, (
            f"Default value must be provided, because {self.typename} does not provide a default value"
        )
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(str(default)),  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=[cc.TextModifier(str(x)) for x in defaults],  # type: ignore
        )

    def to_python_struct(self) -> str:
        """Convert the data type to a python struct format string"""

        assert self.python_struct_format is not None, f"Python struct format string not defined for {self.typename}"

        return self.python_struct_format


class CustomDataType(StandardDataType):
    c_typename: str = Field(description="The C typename that corresponds to the data type")
    string_serialiser: str | None = Field(description="The string serialiser for the data type")
    default: Any | None = Field(description="The default value for the data type")

    model: TypeModelDefinitions = Field(
        description="The model for the data type",
    )

    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        if default is None:
            default = self.default

        assert default is not None, "Default value must be provided, either in the parameter or in the type definition"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=default,  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        assert isinstance(defaults, list), "Defaults must be a list"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=defaults,  # type: ignore
        )

    def extra_extension(self) -> str | None:
        return None

    def resolve_model(self, registry: "UnresolvedTypeRegistry"):
        """Resolve the model for the custom data type"""

        if self.model is None:
            raise ValueError(f"Model for {self.typename} is not defined")

        self.model.resolve(registry)
        self.size = self.get_model_size()

    def get_model_size(self) -> int:
        """Get the size of the model"""
        return struct.calcsize(self.to_python_struct())

    def to_python_struct(self) -> str:
        return self.model.to_struct_format_string()


class BooleanCDataType(StandardDataType):
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, "Default value must be provided"

        if default:
            value = "true"
        else:
            value = "false"

        return super().to_c_initialiser(name, value)

    def to_c_array_initialiser(self, name: str, defaults: List[Any], dimensions: List[int]) -> cc.Variable:
        value = ["true" if x else "false" for x in defaults]

        return super().to_c_array_initialiser(name, value, dimensions)


class CharCDataType(StandardDataType):
    def to_c_initialiser(self, name: str, default: Any) -> cc.Variable:
        assert default is not None, "Default value must be provided"

        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            value=cc.TextModifier(f"'{default}'"),  # type: ignore
        )

    def to_c_array_initialiser(self, name: str, defaults: List[Any] | str | None, dimensions: List[int]) -> cc.Variable:
        if isinstance(defaults, str):
            value = cc.TextModifier(f'"{defaults}"')  # type: ignore
        elif defaults is None:
            value = [cc.TextModifier("0")]  # type: ignore
        else:
            value = [cc.TextModifier(f"'{x}'") for x in defaults]  # type: ignore
        return cc.Variable(
            name=name,
            primitive=self.c_typename,
            array=dimensions,
            value=value,  # type: ignore
        )


BASE_DATA_TYPES: List[DataType] = [
    StandardDataType(typename="u64", size=8, c_typename="uint64_t", python_struct_format="Q"),
    StandardDataType(typename="u32", size=4, c_typename="uint32_t", python_struct_format="I"),
    StandardDataType(typename="u16", size=2, c_typename="uint16_t", python_struct_format="H"),
    StandardDataType(typename="u8", size=1, c_typename="uint8_t", python_struct_format="B"),
    StandardDataType(typename="i64", size=8, c_typename="int64_t", python_struct_format="Q"),
    StandardDataType(typename="i32", size=4, c_typename="int32_t", python_struct_format="I"),
    StandardDataType(typename="i16", size=2, c_typename="int16_t", python_struct_format="H"),
    StandardDataType(typename="i8", size=1, c_typename="int8_t", python_struct_format="B"),
    StandardDataType(typename="f32", size=4, c_typename="float", python_struct_format="f"),
    StandardDataType(typename="f64", size=8, c_typename="double", python_struct_format="d"),
    BooleanCDataType(typename="bool", size=1, c_typename="bool", python_struct_format="?"),
    CharCDataType(typename="char", size=1, c_typename="char", python_struct_format="c"),
]


class UnresolvedTypeRegistry:
    """The type registry, us used to store datatypes, it allows adding custom types"""

    def __init__(self):
        self.types: Dict[str, DataType] = {}

    def register(self, type: DataType | List[DataType]):
        """Register a new type"""

        if isinstance(type, list):
            for t in type:
                self.register(t)
            return

        if type.typename in self.types:
            raise ValueError(f"Type {type.typename} already registered")

        self.types[type.typename] = type

    def get_type(self, name: str) -> DataType:
        """Get a type by name"""

        if name not in self.types:
            raise ValueError(f"Type {name} not found")

        return self.types[name]

    def resolve_models(self):
        """Resolve the models in the registry, this is used to resolve custom types"""

        for type in self.types.values():
            if isinstance(type, CustomDataType) and type.model is not None:
                # Replace with the actual model
                type.resolve_model(self)

    def __repr__(self):
        # Return a list of all type names
        return f"TypeRegistry({', '.join(self.types.keys())})"

    def __getitem__(self, item: str):
        """Get a type by name"""
        return self.get_type(item)

    def __iter__(self):
        """Iterate over the types in the registry"""
        return iter(self.types.items())
