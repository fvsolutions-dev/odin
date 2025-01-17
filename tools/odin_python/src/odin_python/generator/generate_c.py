import csnake as cc

from odin_python.parameter.parameter import (
    RootParameterModel,
)


class CGenerator:
    STORE_TYPE = "root_type_t"
    STORE_NAME = "root"

    RAM_TYPE = "root_ram_t"
    RAM_NAME = "root_ram"

    @staticmethod
    def generate_source(model: RootParameterModel) -> str:
        cw = cc.CodeWriter()
        # Generate the ram storage type
        cw.add_variable_initialization(
            model.to_ram_initialiser(CGenerator.RAM_NAME, CGenerator.RAM_TYPE)
        )
        cw.add_line("")

        value = model.to_c_odin_parameter_initialiser(
            param_name=CGenerator.STORE_NAME, type_name=CGenerator.STORE_TYPE
        )
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
        cw.add_line("")

        cw.add_struct(model.to_ram_typedef(CGenerator.RAM_TYPE))
        cw.add_line("")

        cw.add_struct(model.to_odin_parameter_typedef(type_name=CGenerator.STORE_TYPE))
        cw.add_line("")

        return str(cw)

    @staticmethod
    def generate_single_source(model: RootParameterModel) -> str:
        return (
            CGenerator.generate_header(model) + "\n" + CGenerator.generate_source(model)
        )
