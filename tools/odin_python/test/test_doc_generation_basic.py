from odin_python.data_types.type_registry import BASE_DATA_TYPES, TypeRegistry
from odin_python.doc_generator.generate_doc import (
    DocGenerator,
)
from odin_python.loader import AdvancedLoaderModel
from odin_python.parameter import (
    RootParameterModel,
)


# from
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

    generator = DocGenerator()

    data = generator.generate_single_source(root_parameters,target_file="test.pdf")




if __name__ == "__main__":
    test()
