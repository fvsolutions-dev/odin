import os

import click

from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generator.generate_c import CGenerator
from .loader import AdvancedLoaderModel, SimpleLoaderModel
from odin_python.parameter.parameter import RootParameterModel

DEFAULT_NAME = "OD"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=DEFAULT_NAME, help="Name of the output files")
@click.option("--advanced", is_flag=True, help="Use advanced loader")
def gen_c(input_file: str, output_dir: str, name: str, advanced: bool):
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"

    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"

    print(f"Converting {input_file} to {output_dir}")

    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    if advanced:
        model = AdvancedLoaderModel.from_yaml(input_file)
        root_parameters = RootParameterModel(
            children=model.parameters, access_control=model.access_control, id_space_shift=model.id_space_shift
        )
    else:
        model = SimpleLoaderModel.from_yaml(input_file)
        root_parameters = RootParameterModel(children=model.root, id_space_shift=8)

    root_parameters.post_load_resolve(None, "root", registry)

    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(CGenerator.generate_source(root_parameters, f"{name}.h"))

    with open(os.path.join(output_dir, f"{name}.h"), "w") as f:
        f.write(CGenerator.generate_header(root_parameters))

    print("Conversion complete")


if __name__ == "__main__":
    cli()
