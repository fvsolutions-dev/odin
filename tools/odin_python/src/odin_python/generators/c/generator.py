from io import StringIO
from typing import Literal

import csnake as cc
from pydantic import BaseModel, Field

from odin_python.data_types.type_registry import StandardDataType
from odin_python.generators.abstract_generator import AbstractGenerator, ModelContext
from odin_python.parameter.parameter import (
    ArrayParameterModel,
    BaseBaseParameterModel,
    BaseParameterGroupModel,
    BaseParameterModel,
    C_Names,
    ParameterGroupModel,
    ParameterModel,
    RootParameterModel,
    VectorParameterModel,
)
from odin_python.utils.csnake_custom import StructVariable


def to_variable_initialiser(parameter: BaseParameterModel) -> cc.Variable | None:
    if isinstance(parameter, BaseBaseParameterModel):
        # If the reference is set, then we don't need to initialise the variable
        if parameter.reference:
            return None

        if isinstance(parameter, ParameterModel):
            # If the type is void, then we also don't need to initialise the variable
            if parameter.type == "void":
                return None

            assert isinstance(parameter._resolved_type, StandardDataType)

            return parameter._resolved_type.to_c_initialiser(parameter._name, parameter.default)

        elif isinstance(parameter, ArrayParameterModel):
            assert isinstance(parameter._resolved_type, StandardDataType)

            return parameter._resolved_type.to_c_array_initialiser(
                parameter._name,
                parameter.default if parameter.default else [],  # type: ignore
                [parameter.elements],  # type: ignore
            )

        elif isinstance(parameter, VectorParameterModel):
            data = parameter._resolved_type.to_c_array_initialiser(
                parameter._name, parameter.default, [parameter.max_elements]
            )
            length = len(parameter.default) if parameter.default else 0

            return cc.Variable(
                name=parameter._name,
                primitive="UNKNOWN PRIMITIVE",
                value={"data": data.value, "num_elements": length},  # type: ignore
            )

    elif isinstance(parameter, BaseParameterGroupModel):
        if isinstance(parameter, RootParameterModel):
            assert parameter._c_types is not None, "C types are not set"
            name = parameter._c_types.variables_name
            type = parameter._c_types.variables_type
        else:
            name = parameter._name
            type = "UNKNOWN PRIMITIVE"

        values = {}
        for child in parameter.children.values():
            initialiser = to_variable_initialiser(child)

            if initialiser:
                values[initialiser.name] = initialiser.value

        if len(values) == 0:
            return None

        return cc.Variable(name=name, primitive=type, value=values)  # type: ignore


def to_variable_type(parameter: BaseParameterModel, type_name: str | None = None) -> cc.Struct | None:
    if isinstance(parameter, VectorParameterModel):
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=parameter._name, typedef=False)

        struct.add_variable(
            cc.Variable(
                name="num_elements",
                primitive="size_t",
                value=len(parameter.default) if parameter.default else 0,  # type: ignore
            ),
        )

        struct.add_variable(
            parameter._resolved_type.to_c_array_initialiser("data", parameter.default, [parameter.max_elements])
        )
        return struct

    elif isinstance(parameter, BaseParameterGroupModel):
        if isinstance(parameter, RootParameterModel):
            assert parameter._c_types is not None, "C types are not set"
            struct = StructVariable(name=parameter._c_types.variables_type, typedef=True)
        else:
            struct = StructVariable(var_name=parameter._name, typedef=False)

        items = 0

        for child in parameter.children.values():
            if isinstance(child, ParameterGroupModel):
                variable_type = to_variable_type(child)
                if variable_type:
                    struct.add_struct(variable_type)
                    items += 1

            elif isinstance(child, VectorParameterModel):
                to_variable_initialiser(child)
                variable_type = to_variable_type(child)
                if variable_type:
                    struct.add_struct(variable_type)
                    items += 1

            elif isinstance(child, ParameterModel) or isinstance(child, ArrayParameterModel):
                variable = to_variable_initialiser(child)
                if variable:
                    struct.add_variable(variable)
                    items += 1

            else:
                raise ValueError("Unknown type")

        if items == 0:
            return None

        return struct

    else:
        raise ValueError("Unknown type")


class CGenerator(AbstractGenerator):
    class Config(BaseModel):
        objects_type: str = "odin_objects"
        objects_name: str = "odin_objects_t"
        variables_type: str = "odin_variables"
        variables_name: str = "odin_variables_t"
        groups_name: str = "odin_store"

        extra_includes: list[str] = Field(
            default_factory=list,
        )
        header_file_name: str = Field(
            default="OD.h",
        )
        src_file_name: str = Field(
            default="OD.c",
        )

        @property
        def types(self) -> C_Names:
            return C_Names(
                objects_name=self.objects_name,
                objects_type=self.objects_type,
                variables_name=self.variables_name,
                variables_type=self.variables_type,
                groups_name=self.groups_name,
            )

    config: Config

    def __init__(self, config: Config):
        super().__init__(config)
        self.config = config

    def generate(  # type: ignore
        self,
        model_context: ModelContext,
        output_path: str | StringIO,
        type: Literal["header", "source", "single_source"] = "header",
        **kwargs: dict[str, str],
    ) -> None:
        if type == "header":
            data = self.generate_header(model_context)
        elif type == "source":
            data = self.generate_source(model_context)
        elif type == "single_source":
            data = self.generate_header(model_context) + "\n" + self.generate_source(model_context, no_include=True)
        else:
            raise ValueError(f"Unknown type: {type}")

        self.save_to_file(output_path, data)

    def generate_source(self, model_context: ModelContext, no_include: bool = False) -> str:
        cw = cc.CodeWriter()

        if not no_include:
            cw.add_line(f'#include "{self.config.header_file_name}"')
            cw.add_line("")

        model_context.root_model.initialise_types(self.config.types)

        # Generate the ram storage type
        initaliser = to_variable_initialiser(model_context.root_model)
        assert initaliser is not None, "Initialiser empty"

        cw.add_variable_initialization(initaliser)  # type: ignore
        cw.add_line("")

        value = model_context.root_model.to_object_initialiser()

        value.qualifiers = ["const"]
        cw.add_variable_initialization(value)
        cw.add_line("")

        values = model_context.root_model.to_group_initialiser()
        for value in values:
            value.qualifiers = ["const"]
            cw.add_variable_initialization(value)
            cw.add_line("")

        return str(cw)

    def generate_header(self, model_context: ModelContext) -> str:
        cw = cc.CodeWriter()
        cw.add_line("#include <stdint.h>")
        cw.add_line("#include <stdbool.h>")
        cw.add_line("#include <odin.h>")
        cw.add_line("#include <odin_core.h>")
        cw.add_line("#include <odin_security.h>")

        for include in self.config.extra_includes:
            cw.add_line(f'#include "{include}"')

        # Add include guard
        cw.add_line(f"#ifndef {self.config.header_file_name.upper().replace('.', '_')}_H")
        cw.add_line(f"#define {self.config.header_file_name.upper().replace('.', '_')}_H")
        cw.add_line("")

        model_context.root_model.initialise_types(self.config.types)

        cw.add_struct(to_variable_type(model_context.root_model))  # type: ignore
        cw.add_line("")

        cw.add_struct(model_context.root_model.to_object_type())
        cw.add_line("")

        # Generate acces control definitions
        for line in model_context.root_model.to_access_control_header():
            cw.add_line(line)

        # Add external references
        initaliser = to_variable_initialiser(model_context.root_model)
        assert initaliser is not None, "Initialiser empty"

        cw.add_variable_declaration(initaliser, extern=True)

        value = model_context.root_model.to_object_initialiser()
        value.qualifiers = ["const"]

        cw.add_variable_declaration(
            value,
            extern=True,
        )

        for value in model_context.root_model.to_group_initialiser():
            value.qualifiers = ["const"]
            cw.add_variable_declaration(
                value,
                extern=True,
            )

        cw.add_line("")
        cw.add_line("#endif /* {model.header_name.upper()}_H */")
        cw.add_line("")
        return str(cw)
