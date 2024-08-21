from .generate_c import generate_header, generate_source
from .generate_docs import generate_md_file
from .models import MainModel
from pydantic_yaml import parse_yaml_file_as
import click
import os

NAME = "ODin"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=NAME, help="Name of the output files")
def gen_c(input_file: str, output_dir: str, name: str) -> None:
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"
    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"
    print(f"Converting {input_file} to {output_dir}")

    config: MainModel = parse_yaml_file_as(MainModel, input_file)

    # Write to file
    with open(os.path.join(output_dir, f"{name}.h"), "w") as f:
        f.write(generate_header(config))

    # Write to file
    with open(os.path.join(output_dir, f"{name}.c"), "w") as f:
        f.write(generate_source(config))

    print("Conversion complete")


@cli.command()
@click.argument("input_file")
@click.argument("output_dir")
@click.option("name", "--name", default=NAME, help="Name of the output files")
def gen_md(input_file: str, output_dir: str, name: str) -> None:
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"
    assert os.path.exists(output_dir), f"Output directory {output_dir} does not exist"
    # Check if the input file is a valid yaml file
    assert input_file.endswith(".yaml"), "Input file must be a yaml file"
    print(f"Converting {input_file} to {output_dir}")

    config: MainModel = parse_yaml_file_as(MainModel, input_file)
    output_path = os.path.join(output_dir, f"{name}.md")

    # Write to file
    generate_md_file(output_path, config)


if __name__ == "__main__":
    cli()
