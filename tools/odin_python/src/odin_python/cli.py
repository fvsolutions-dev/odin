import os

import click
from pydantic_yaml import parse_yaml_file_as

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generator.generate_c import CGenerator
from odin_python.loader import LoaderModel
from odin_python.parameter.parameter import RootParameterModel

DEFAULT_NAME = "OD"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=DEFAULT_NAME, help="Name of the output files")
def gen_c(input_file: str, output_dir: str, name: str) -> None:
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"

    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"

    print(f"Converting {input_file} to {output_dir}")

    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    model = LoaderModel.from_yaml(input_file)

    root_parameters = RootParameterModel(children=model.root)  # type: ignore
    root_parameters.post_load_resolve(None, "root", registry)

    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(CGenerator.generate_source(root_parameters, f"{name}.h"))

    with open(os.path.join(output_dir, f"{name}.h"), "w") as f:
        f.write(CGenerator.generate_header(root_parameters))

    print("Conversion complete")


if __name__ == "__main__":
    cli()
