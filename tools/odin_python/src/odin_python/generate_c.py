import os

import click
from csnake import CodeWriter
from .models import (
    AccessOptionsGenerator,
    MainModel,
)
from pydantic_yaml import parse_yaml_file_as


def generate_header(config: MainModel) -> str:
    # Generate the output.h file
    cw = CodeWriter()
    cw.add_line("#include <stdint.h>")
    cw.add_line('#include "odin_datastore.h"')
    cw.add_line("")

    opt_gen = AccessOptionsGenerator(config)
    opt_gen.add_define_macros(cw)
    opt_gen.add_log_reference(cw)

    # Add the variable struct
    cw.add_struct(config.as_variable_struct())
    cw.add_line("")

    # Add the parameter struct
    cw.add_struct(config.as_parameter_store_struct())
    cw.add_line("")

    # Add extern variable declarations
    cw.add_variable_declaration(
        config.as_variable(),
        extern=True,
    )
    cw.add_variable_declaration(config.as_parameter_store(opt_gen), extern=True)

    for group in config.datastore.values():
        cw.add_variable_declaration(group.as_reference(), extern=True)

    cw.add_variable_declaration(config.as_reference(), extern=True)

    return str(cw)


def generate_source(config: MainModel) -> str:
    # Generate the output.c file
    cw = CodeWriter()
    cw.add_line("#include <stdint.h>")
    cw.add_line('#include "odin_datastore.h"')
    cw.add_line('#include "ODin.h"')
    cw.add_line("")


    opt_gen = AccessOptionsGenerator(config)
    # Create opt_gen
    opt_gen.add_log_values(cw)

    # Add reference definitions
    for group in config.datastore.values():
        for param in group.data.values():
            if param.extension:
                value = param.extension.required_references()
                if value:
                    cw.add_line(value)
    cw.add_line("")

    cw.add_variable_initialization(config.as_variable())
    cw.add_line("")

    cw.add_variable_initialization(config.as_parameter_store(opt_gen))
    cw.add_line("")

    for group in config.datastore.values():
        cw.add_variable_initialization(group.as_reference())
        cw.add_line("")

    cw.add_variable_initialization(config.as_reference())

    file = str(cw)
    return file

