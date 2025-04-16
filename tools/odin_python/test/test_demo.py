from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.c_generator.generate_c import (
    CGenerator,
)
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)
from odin_python.odin_db_generator import ODIN_DB_generator


import subprocess

import pytest
import glob


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

    with open(f"{config}.json", "w") as f:
        f.write(
            ODIN_DB_generator.generate_single_source(root_parameters, registry)  # type: ignore
        )
    

    return f"{config}.c"




if __name__ == "__main__":
    CONFIGS = [r"test/demo/object_dictonary.yaml"]

    for config in CONFIGS:
        print(f"processing {config}")
        file = process_config(config)
