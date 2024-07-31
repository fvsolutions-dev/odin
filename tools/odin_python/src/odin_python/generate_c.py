import os

import click
from csnake import CodeWriter
from .models import AccessOptionsGenerator, MainModel, DeviceGroupModel
from pydantic_yaml import parse_yaml_file_as
from typing import List


def convert_to_virtual_group(
    config: MainModel, group_name: str, parameters: List[str]
) -> DeviceGroupModel:
    _group = DeviceGroupModel(
        id=0x00,
        _name=group_name,
        _variable_names=config.variable_names,
        description="",
        data={},
        access_permissions={},
    )

    # This should not be needed, dont know why
    _group._name = group_name
    _group._variable_names = config.variable_names

    # Find all the parameters in the group
    for param in parameters:
        group_name, param_name = param.split(".")
        if group_name not in config.datastore:
            raise ValueError(f"Group {group_name} does not exist in the datastore")

        if param_name not in config.datastore[group_name].data:
            raise ValueError(
                f"Parameter {param_name} does not exist in group {group_name}"
            )

        _group.data[param_name] = config.datastore[group_name].data[param_name]

    return _group


def generate_header(config: MainModel) -> str:
    # Generate the output.h file
    cw = CodeWriter()
    cw.add_line("#include <stdint.h>")
    cw.add_line('#include "odin_datastore.h"')
    cw.add_line('#ifndef ODIN_DATASTORE_H_')
    cw.add_line('#define ODIN_DATASTORE_H_')
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


    # Generate groups
    for group_name, parameters in config.groups.items():
        _group = convert_to_virtual_group(config, group_name, parameters)
        cw.add_variable_declaration(_group.as_reference(), extern=True)

    cw.add_line("#endif")

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
    cw.add_line("")

    # Generate groups
    for group_name, parameters in config.groups.items():
        _group = convert_to_virtual_group(config, group_name, parameters)
        cw.add_variable_initialization(_group.as_reference())

    file = str(cw)
    return file
