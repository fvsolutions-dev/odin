from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.generators.abstract_generator import ModelContext
from odin_python.generators.generator import default_generator
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)


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


    default_generator(
        name="test",
        model_context=ModelContext(
            root_model=root_parameters,
            types=registry,
        ),
        output_dir="test/demo",
        doc=True,
        db=True,
        py=True,
        c=True,
    )


if __name__ == "__main__":
    CONFIGS = [r"test/demo/object_dictonary.yaml"]

    for config in CONFIGS:
        print(f"processing {config}")
        process_config(config)
