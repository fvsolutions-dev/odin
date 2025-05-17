from odin_python.generators.generator import default_generator
from odin_python.parameter.loader import ConfigurationReader


def process_config(config: str):
    reader = ConfigurationReader()
    model_context, config_model = reader.load(config, "advanced")
    default_generator(
        name="test",
        model_context=model_context,
        output_dir="test/demo",
        doc=True,
        db=True,
        py=True,
        c=True,
        generator_config=config_model,
    )


if __name__ == "__main__":
    CONFIGS = [r"test/demo/object_dictonary.yaml"]

    for config in CONFIGS:
        print(f"processing {config}")
        process_config(config)
