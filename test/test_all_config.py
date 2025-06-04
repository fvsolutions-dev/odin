from odin_python.parameter.loader import ConfigurationReader
from odin_python.generators.generator import GeneratorTarget, generator
from pathlib import Path


def process_config(config_file: Path):
    model_context, config_model = ConfigurationReader().load(config_file.as_posix(), "advanced")

    output_dir = Path("test/demo") / config_file.stem

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

def test_all_configs():
    """Test all configurations in the test/test_configs directory."""
    CONFIGS = Path("test/test_configs").glob("*.yaml")

    for config in CONFIGS:
        print(f"processing config: '{config}")
        process_config(config)
        

if __name__ == "__main__":
    CONFIGS = Path("test/test_configs").glob("*.yaml")

    for config in CONFIGS:
        print(f"processing config: '{config}")
        process_config(config)
