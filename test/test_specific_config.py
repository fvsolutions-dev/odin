from odin_python.parameter.loader import ConfigurationReader
from odin_python.generators.generator import GeneratorTarget, generator
from pathlib import Path


CONFIG = Path(__file__).parent / "test_configs" / "test_as_array.yaml"


def process_config(config_file: Path):
    model_context, config_model = ConfigurationReader().load(config_file.as_posix(), "advanced")

    output_dir = Path(__file__) .parent / "demo"/ config_file.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    for target in GeneratorTarget.all():
        print(f" - creating target '{target.name}'")
        generator(
            name="OD",
            model_context=model_context,
            output_dir=output_dir.as_posix(),
            target=target,
            generator_config=config_model,
        )


if __name__ == "__main__":
    process_config(CONFIG)
