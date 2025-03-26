from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.c_generator.generate_c import (
    CGenerator,
)
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)


import subprocess

import pytest
import glob


CONFIGS = glob.glob("test/advanced_configs/*.yaml")


def process_config(config: str):
    model = AdvancedLoaderModel.from_yaml(config)
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)
    model.types.register_types(registry)

    root_parameters = RootParameterModel(
      children=model.parameters,
        access_control=model.access_control,
        id_space_shift=model.id_space_shift,
    )  # type: ignore
    root_parameters.post_load_resolve(None, "root", registry)

    with open(f"{config}.c", "w") as f:
        f.write(
            CGenerator.generate_single_source(
                root_parameters, extra_includes=model.c_include
            )
        )

    return f"{config}.c"


def compile_file(file: str):
    command = f"clang -o {file}.o -c {file} -I ../../src -I test/advanced_configs"
    print(command)
    e = subprocess.run(command, shell=True)
    if e.returncode != 0:
        raise Exception(f"`Failed to compile {file}")


# Parameterize with all the configs
@pytest.mark.parametrize("config", CONFIGS)
def test_advanced_parse(config: str):
    file = process_config(config)
    compile_file(file)


@pytest.mark.parametrize(
    "config", glob.glob("test/advanced_configs/acces_control_negative_configs/*.yaml")
)
def test_advanced_parse_negative(config: str):
    with pytest.raises(Exception):
        file = process_config(config)
        compile_file(file)


@pytest.mark.parametrize(
    "config", glob.glob("test/advanced_configs/parameter_space_negative_configs/*.yaml")
)
def test_parameter_space_parse_negative(config: str):
    with pytest.raises(Exception):
        file = process_config(config)
        compile_file(file)


if __name__ == "__main__":
    # CONFIGS = [r"test\advanced_configs\1_access_control.yaml"]
    CONFIGS = [r"test\advanced_configs\4_custom_data_types.yaml"]

    for config in CONFIGS:
        print(f"processing {config}")
        file = process_config(config)
        compile_file(file)
