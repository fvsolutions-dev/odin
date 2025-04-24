from odin_python.data_types.type_registry import BASE_DATA_TYPES, UnresolvedTypeRegistry
from odin_python.generators.generator import (
    DocGenerator,
)
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)


# from
def test():
    model = AdvancedLoaderModel.from_yaml(r"test\advanced_configs\5_bunch_of_params.yaml")

    registry = UnresolvedTypeRegistry()
    registry.register(BASE_DATA_TYPES)
    model.types.register_types(registry)

    root_parameters = RootParameterModel(
        children=model.parameters,
        access_control=model.access_control,
        id_space_shift=model.id_space_shift,
    )  # type: ignore

    root_parameters.post_load_resolve(None, "root", registry)

    generator = DocGenerator()

    generator.generate_single_source(root_parameters, target_file="test.pdf")


if __name__ == "__main__":
    test()
