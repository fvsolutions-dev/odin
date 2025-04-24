from pydantic import BaseModel, Field, RootModel
from typing import Any, Dict
from .type_registry import CustomDataType, TypeRegistry


class TypeModel(BaseModel):
    typename: str
    string_serialiser: str | None = Field(description="The string serialiser for the data type", default=None)
    default: Any | None = Field(description="The default value for the data type", default=None)
    size: int = Field(description="Size of the data type in bytes")


class CustomTypeModel(BaseModel):
    class TypeDefaultModel(BaseModel):
        type: str
        default: Any | None = Field(description="The default value for the data type", default=None)

    typename: str
    string_serialiser: str | None = Field(description="The string serialiser for the data type", default=None)
    model: dict[str, str | TypeDefaultModel] = Field(
        description="The model for the data type",
    )
    default: Any | None = Field(description="The default value for the data type", default=None)


class TypeDefinitionsModel(RootModel[Dict[str, TypeModel | CustomTypeModel]]):
    @classmethod
    def empty(cls):
        return TypeDefinitionsModel(root={})

    def register_types(self, registry: TypeRegistry):
        for type_name, type_model in self.root.items():
            if isinstance(type_model, TypeModel):
                registry.register(
                    CustomDataType(
                        typename=type_name,
                        c_typename=type_model.typename,
                        py_typename=type_model.typename,
                        default=type_model.default,
                        size=type_model.size,
                        string_serialiser=type_model.string_serialiser,
                        model=None,
                    )
                )
            elif isinstance(type_model, CustomTypeModel):
                registry.register(
                    CustomDataType(
                        typename=type_name,
                        c_typename=type_model.typename,
                        py_typename=type_model.typename,
                        default=type_model.default,
                        size=-1,
                        string_serialiser=type_model.string_serialiser,
                        model=type_model.model,
                    )
                )

        # Resolve the models
        registry.resolve_models()
