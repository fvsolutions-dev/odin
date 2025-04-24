from pydantic import BaseModel, Field, RootModel
from typing import Any, Dict
from .type_registry import CustomDataType, TypeModelDefinitions, UnresolvedTypeRegistry


class TypeSpecificationModel(BaseModel):
    typename: str
    string_serialiser: str | None = Field(description="The string serialiser for the data type", default=None)
    model: TypeModelDefinitions = Field(
        description="The model for the data type",
    )
    default: Any | None = Field(description="The default value for the data type", default=None)


class TypeSpecifciationCollectionModel(RootModel[Dict[str, TypeSpecificationModel]]):
    @classmethod
    def empty(cls):
        return TypeSpecifciationCollectionModel(root={})

    def register_types(self, registry: UnresolvedTypeRegistry):
        for type_name, type_model in self.root.items():
            registry.register(
                CustomDataType(
                    typename=type_name,
                    c_typename=type_model.typename,
                    default=type_model.default,
                    size=-1,
                    string_serialiser=type_model.string_serialiser,
                    model=type_model.model,
                )
            )