import json
import os

import click

from .generators.generator import default_generator
from .parameter.loader import AdvancedLoaderModel, SimpleLoaderModel, ConfigurationReader

DEFAULT_NAME = "OD"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=DEFAULT_NAME, help="Name of the output files")
@click.option("--advanced", is_flag=True, help="Use advanced loader")
@click.option("--doc", is_flag=True, help="Generate documentation")
@click.option("--db", is_flag=True, help="Generate database")
@click.option("--py", is_flag=True, help="Generate python code")
@click.option("--c", is_flag=True, help="Generate C code")
def generate(input_file: str, output_dir: str, name: str, advanced: bool, doc: bool, db: bool, py: bool, c: bool):
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"

    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"

    print(f"Converting {input_file} to {output_dir}")

    reader = ConfigurationReader()
    model_context, config_model = reader.load(input_file, "advanced" if advanced else "simple")

    default_generator(
        name=name,
        model_context=model_context,
        output_dir=output_dir,
        doc=doc,
        db=db,
        py=py,
        c=c,
        generator_config=config_model,
    )


@cli.command()
@click.argument("output_file")
@click.option("--advanced", is_flag=True, help="Use advanced loader")
def gen_schema(output_file: str, advanced: bool = False):
    with open(output_file, "w") as f:
        if advanced:
            f.write(json.dumps(AdvancedLoaderModel.model_json_schema(), indent=4))
        else:
            f.write(json.dumps(SimpleLoaderModel.model_json_schema(), indent=4))


if __name__ == "__main__":
    cli()
