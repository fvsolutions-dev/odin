from typing import Dict

from pydantic import BaseModel, Field, RootModel
from typing import Any, List


class TypeAndDefaultModel(BaseModel):
    type: "list[str] | str"
    default: "list[Any] | Any" = Field(description="The default value for the data type")


class TypeModel(RootModel["str | list[str]"]):
    pass


class TypeModelDefinitions(
    RootModel[
        Dict[
            str,
            "TypeAndDefaultModel | TypeModel  | TypeModelDefinitions",
        ]
        | TypeModel
        | TypeAndDefaultModel
    ],
):
    pass


class DataTypeDefintion(BaseModel):
    class Config:
        extra = "forbid"

    description: str = Field(description="Description of the data type", default="Not specified")
    string_serialiser: str | None = Field(default=None, description="The string serialiser extension for the data type")

    c_typename: str | None = Field(
        default=None,
        description="The C typename that corresponds to the data type, if not specified _t will be added to the name",
    )
    py_typename: str | None = Field(
        default=None,
        description="The Python typename that corresponds to the data type ifnot specified the type will be camelcased with a Odin prefix",
    )

    model: TypeModelDefinitions = Field(
        description="The model for the data type",
    )
