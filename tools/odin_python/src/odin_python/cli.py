import os

import click
import json
from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generators.abstract_generator import ModelContext
from .generators.generator import default_generator
from .loader import AdvancedLoaderModel, SimpleLoaderModel
from odin_python.parameter import RootParameterModel

DEFAULT_NAME = "OD"


@click.group()
def cli():
    pass


def load_model(input_file: str, advanced: bool):
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)

    if advanced:
        model = AdvancedLoaderModel.from_yaml(input_file)
        model.types.register_types(registry)

        root_parameters = RootParameterModel(
            children=model.parameters,
            access_control=model.access_control,
            id_space_shift=model.id_space_shift,
        )

    else:
        model = SimpleLoaderModel.from_yaml(input_file)
        root_parameters = RootParameterModel(children=model.root, id_space_shift=8)

    root_parameters.post_load_resolve(None, "root", registry)

    return model, root_parameters, registry


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

    model, root_parameters, registry = load_model(input_file, advanced)

    default_generator(
        name=name,
        model_context=ModelContext(
            root_model=root_parameters,
            types=registry,
        ),
        output_dir=output_dir,
        doc=doc,
        db=db,
        py=py,
        c=c,
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
