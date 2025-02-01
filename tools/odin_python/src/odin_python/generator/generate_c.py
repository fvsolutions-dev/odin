import csnake as cc

from odin_python.parameter import (
    RootParameterModel,
)


class CGenerator:
    STORE_TYPE = "root_type_t"
    STORE_NAME = "root"

    RAM_TYPE = "root_ram_t"
    RAM_NAME = "root_ram"

    BASE_GROUP_NAME = "odin_store"

    @staticmethod
    def generate_source(model: RootParameterModel, header_name: str | None) -> str:
        cw = cc.CodeWriter()

        if header_name:
            cw.add_line(f'#include "{header_name}"')

        cw.add_line("")

        # Generate the ram storage type
        cw.add_variable_initialization(
            model.to_ram_initialiser(CGenerator.RAM_NAME, CGenerator.RAM_TYPE)
        )
        cw.add_line("")

        value = model.to_c_odin_parameter_initialiser(
            param_name=CGenerator.STORE_NAME,
            type_name=CGenerator.STORE_TYPE,
            absolute_reference="",
        )
        value.qualifiers = ["const"]
        cw.add_variable_initialization(value)
        cw.add_line("")

        values = model.to_c_odin_parameter_group_initialiser(
            param_name=CGenerator.BASE_GROUP_NAME
        )
        for value in values:
            value.qualifiers = ["const"]
            cw.add_variable_initialization(value)
            cw.add_line("")

        return str(cw)

    @staticmethod
    def generate_header(model: RootParameterModel) -> str:
        cw = cc.CodeWriter()
        cw.add_line("#include <stdint.h>")
        cw.add_line("#include <stdbool.h>")
        cw.add_line("#include <odin.h>")
        cw.add_line("#include <odin_security.h>")
        cw.add_line("")

        cw.add_struct(model.to_ram_typedef(CGenerator.RAM_TYPE))
        cw.add_line("")

        cw.add_struct(model.to_odin_parameter_typedef(type_name=CGenerator.STORE_TYPE))
        cw.add_line("")

        # Generate acces control definitions
        for line in model.to_access_control_header():
            cw.add_line(line)

        # Add external references
        cw.add_variable_declaration(
            model.to_ram_initialiser(CGenerator.RAM_NAME, CGenerator.RAM_TYPE),
            extern=True,
        )

        value = model.to_c_odin_parameter_initialiser(
            param_name=CGenerator.STORE_NAME,
            type_name=CGenerator.STORE_TYPE,
            absolute_reference="",
        )
        value.qualifiers = ["const"]
        cw.add_variable_declaration(
            value,
            extern=True,
        )

        for value in model.to_c_odin_parameter_group_initialiser(
            param_name=CGenerator.BASE_GROUP_NAME
        ):
            value.qualifiers = ["const"]
            cw.add_variable_declaration(
                value,
                extern=True,
            )

        return str(cw)

    @staticmethod
    def generate_single_source(model: RootParameterModel) -> str:
        return (
            CGenerator.generate_header(model)
            + "\n"
            + CGenerator.generate_source(model, None)
        )
