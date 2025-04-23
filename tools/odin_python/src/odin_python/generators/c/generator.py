from typing import Literal
import csnake as cc

from io import StringIO

from odin_python.parameter.parameter import C_Names
from ..abstract_generator import AbstractGenerator, ModelContext
from pydantic import BaseModel, Field


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
            data = self.generate_header(model_context) + "\n" + self.generate_source(model_context,no_include=True)
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
        cw.add_variable_initialization(model_context.root_model.to_variable_initialiser())
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

        cw.add_struct(model_context.root_model.to_variable_type()) # type: ignore
        cw.add_line("")

        cw.add_struct(model_context.root_model.to_object_type())
        cw.add_line("")

        # Generate acces control definitions
        for line in model_context.root_model.to_access_control_header():
            cw.add_line(line)

        # Add external references
        cw.add_variable_declaration(
            model_context.root_model.to_variable_initialiser(),
            extern=True,
        )

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
