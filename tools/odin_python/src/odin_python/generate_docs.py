#!/usr/bin/env python3
import os
from typing import Dict, Union

from .models import MainModel, ParameterModel
from pydantic_yaml import parse_yaml_file_as


def perm_to(data: Dict[str, Union[str, Dict]]) -> str:
    bullet_list = ""
    for key, value in data.items():
        bullet_list += f"{key}-{value} "

    return bullet_list


def format_primitive(parameter: ParameterModel) -> str:
    if parameter.length is None:
        return parameter.primitive
    return f"{parameter.primitive}[{parameter.length}]"


def format_value(parameter: ParameterModel) -> str:
    if parameter.format == "INT":
        return f"{parameter.default}"

    if parameter.format == "FLOAT":
        return f"{parameter.default}"

    if parameter.format == "UTF8":
        return f"'{parameter.default}'"

    if "HEX" in parameter.format:
        if isinstance(parameter.default, int):
            return f"{parameter.default:#06x}"

        if isinstance(parameter.default, str):
            return f"{int(parameter.default, 16):#06x}"

        if isinstance(parameter.default, list):
            print(parameter.default)

    return f"{parameter.default}"


def get_id(parameter: ParameterModel) -> str:
    return f"{parameter.qualified_id:#06x}"


def get_group_id(parameter: ParameterModel) -> str:
    return f"{parameter.id:#06x}"


def generate_md_file(output_path: str, data: MainModel):
    from mdutils import MdUtils

    mdFile = MdUtils(file_name=output_path, title="Tilt bike object dictionary")

    mdFile.new_header(level=1, title="Groups")
    # Create table containg all groups
    table_header = ["Group ID", "Name"]
    table_content = []
    table_content.extend(table_header)
    for group_name, parameter_group in data.datastore.items():
        table_content.extend([get_group_id(parameter_group), group_name])

    table = mdFile.new_table(
        columns=len(table_header),
        rows=len(data.datastore) + 1,
        text=table_content,
        text_align="left",
    )

    for group_name, parameter_group in data.datastore.items():
        mdFile.new_header(level=1, title=f"Group: '{group_name}'")
        mdFile.new_paragraph(parameter_group.description)
        mdFile.new_line()
        table_header = ["Sub ID", "ID", "Name", "Permissions", "Primitive", "Default"]
        table_content = []
        table_content.extend(table_header)
        for parameter_name, parameter in parameter_group.data.items():
            table_content.extend(
                [
                    parameter.id,
                    get_id(parameter),
                    parameter_name,
                    perm_to(parameter.access_permissions),
                    format_primitive(parameter),
                    format_value(parameter),
                ]
            )

        mdFile.new_table(
            columns=len(table_header),
            rows=len(parameter_group.data) + 1,
            text=table_content,
            text_align="left",
        )

        mdFile.new_line()
        # Add all the descriptions

        for parameter_name, parameter in parameter_group.data.items():
            mdFile.new_header(level=2, title=parameter_name)
            # Underline
            # mdFile.new_paragraph("**Info**")
            # # Create bullet list
            # mdFile.new_list(
            #     [
            #         f" **ID**: {get_id(parameter)}",
            #         " **Permissions**:",
            #         [
            #             f"{key} {value}"
            #             for key, value in parameter.access_permissions.items()
            #         ],
            #         f" **Default**: {parameter.default}",
            #         f" **Primitive**: {format_primitive(parameter)}",
            #         f" **Length**: {parameter.length}",
            #         f" **Format**: {parameter.format}",

            #     ]
            # )

            mdFile.new_paragraph(f"**Description** \n {parameter.description}")
            mdFile.new_line()

        # signal new page
        mdFile.new_paragraph("\\newpage")

    mdFile.create_md_file()

    return os.path.abspath(output_path)


def main():
    input_file = r"D:\projects\mouverti\esp_gatt_test\bleprph\main\app_datastore\datastore_config.yaml"

    config: MainModel = parse_yaml_file_as(MainModel, input_file)

    output_name = "output.md"
    outFile = generate_md_file(output_name, config)


if __name__ == "__main__":
    main()
