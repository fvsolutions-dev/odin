import os
from enum import Enum
from typing import Any, Dict, List, Literal, Union

import click
import csnake as cc
from csnake import CodeWriter, CodeWriterLite, FormattedLiteral, Variable
from csnake_custom import StructVariable
from models import (
    AccessOptions,
    AccessOptionsGenerator,
    ConfigModel,
    DeviceGroupModel,
    ParameterModel,
)
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as
from strenum import StrEnum


def generate_header(config: ConfigModel) -> str:
    # Generate the output.h file
    cw = CodeWriter()
    cw.add_line("#include <stdint.h>")
    cw.add_line('#include "odin_datastore.h"')
    cw.add_line("")

    opt_gen = AccessOptionsGenerator(config)
    opt_gen.add_define_macros(cw)

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


def generate_source(config: ConfigModel) -> str:
    # Generate the output.c file
    cw = CodeWriter()
    cw.add_line("#include <stdint.h>")
    cw.add_line('#include "ODin.h"')
    cw.add_line('#include "odin_datastore.h"')
    cw.add_line("")

    opt_gen = AccessOptionsGenerator(config)

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


NAME = "ODin"


@click.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=NAME, help="Name of the output files")
def main(input_file: str, output_dir: str, name: str) -> None:
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"
    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"
    print(f"Converting {input_file} to {output_dir}")

    config: ConfigModel = parse_yaml_file_as(ConfigModel, input_file)

    # Write to file
    with open(os.path.join(output_dir, f"{name}.h"), "w") as f:
        f.write(generate_header(config))

    # Write to file
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(generate_source(config))

    print("Conversion complete")


if __name__ == "__main__":
    main()
