import csnake as cc

from odin_python.parameter import (
    RootParameterModel,
)
from odin_python.parameter.parameter import C_Names


class CGenerator:
    TYPES = C_Names(
        objects_name="odin_objects",
        objects_type="odin_objects_t",
        variables_name="odin_variables",
        variables_type="odin_variables_t",
        groups_name="odin_store",
    )

    @staticmethod
    def generate_source(model: RootParameterModel, header_name: str | None) -> str:
        cw = cc.CodeWriter()

        if header_name:
            cw.add_line(f'#include "{header_name}"')

        cw.add_line("")

        model.initialise_types(CGenerator.TYPES)
        # Generate the ram storage type
        cw.add_variable_initialization(model.to_variable_initialiser())
        cw.add_line("")

        value = model.to_object_initialiser()

        value.qualifiers = ["const"]
        cw.add_variable_initialization(value)
        cw.add_line("")

        values = model.to_group_initialiser()

        for value in values:
            value.qualifiers = ["const"]
            cw.add_variable_initialization(value)
            cw.add_line("")

        return str(cw)

    @staticmethod
    def generate_header(
        model: RootParameterModel, extra_includes: list[str] | None = None, header_name: str | None = None
    ) -> str:
        cw = cc.CodeWriter()
        cw.add_line("#include <stdint.h>")
        cw.add_line("#include <stdbool.h>")
        cw.add_line("#include <odin.h>")
        cw.add_line("#include <odin_core.h>")
        cw.add_line("#include <odin_security.h>")
        if extra_includes:
            for include in extra_includes:
                cw.add_line(f'#include "{include}"')
       
        if not header_name:
            header_name = "ODIN_GENERATED"
            
        # Add include guard
        cw.add_line(f"#ifndef {header_name.upper()}_H")
        cw.add_line(f"#define {header_name.upper()}_H")
        cw.add_line("")

        model.initialise_types(CGenerator.TYPES)
        
        cw.add_struct(model.to_variable_type())
        cw.add_line("")

        cw.add_struct(model.to_object_type())
        cw.add_line("")

        # Generate acces control definitions
        for line in model.to_access_control_header():
            cw.add_line(line)

        # Add external references
        cw.add_variable_declaration(
            model.to_variable_initialiser(),
            extern=True,
        )

        value = model.to_object_initialiser()
        value.qualifiers = ["const"]

        cw.add_variable_declaration(
            value,
            extern=True,
        )

        for value in model.to_group_initialiser():
            value.qualifiers = ["const"]
            cw.add_variable_declaration(
                value,
                extern=True,
            )

        cw.add_line("")
        cw.add_line("#endif /* {model.header_name.upper()}_H */")
        cw.add_line("")
        return str(cw)

    @staticmethod
    def generate_single_source(
        model: RootParameterModel, extra_includes: list[str] | None = None
    ) -> str:
        return (
            CGenerator.generate_header(model, extra_includes=extra_includes)
            + "\n"
            + CGenerator.generate_source(model, None)
        )
