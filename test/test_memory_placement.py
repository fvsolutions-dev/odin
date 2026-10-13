from pathlib import Path

from odin_python.generators.generator import GeneratorTarget, generator
from odin_python.parameter.loader import ConfigurationReader

CONFIG = Path(__file__).parent / "test_configs" / "memory_placement.yaml"


def test_memory_placement(tmp_path: Path):
    model_context, config_model = ConfigurationReader().load(CONFIG.as_posix(), "advanced")
    generator(
        name="OD",
        model_context=model_context,
        output_dir=tmp_path.as_posix(),
        target=GeneratorTarget.C,
        generator_config=config_model,
    )
    source = (tmp_path / "OD.c").read_text()
    header = (tmp_path / "OD.h").read_text()

    # data_attributes + no_init: placed in the section, no initializer
    assert 'odin_variables_t odin_variables __attribute__((section(".shared")));' in source
    # default_object: the defaults as a separate const object
    assert "const odin_variables_t odin_defaults = {" in source
    assert ".speed = 42" in source
    assert "extern const odin_variables_t odin_defaults;" in header
