from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.py_generator.generate_py import (
    PYGenerator,
)
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)


def test():
    model = AdvancedLoaderModel.from_yaml(r"test\advanced_configs\5_bunch_of_params.yaml")

    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)
    model.types.register_types(registry)

    root_parameters = RootParameterModel(
        children=model.parameters,
        access_control=model.access_control,
        id_space_shift=model.id_space_shift,
    )  # type: ignore

    root_parameters.post_load_resolve(None, "root", registry)

    generator = PYGenerator()

    data = generator.generate_single_source(root_parameters)

    with open(r"test.py", "w") as f:
        f.write(data)


if __name__ == "__main__":
    test()
