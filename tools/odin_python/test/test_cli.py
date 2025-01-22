import os
import glob
import pytest
from click.testing import CliRunner
from src.odin_python.cli import cli

CONFIGS = glob.glob("test/configs/*.yaml")

TEMP_OUTPUT_DIR = "test/output"

@pytest.mark.parametrize("config_file", CONFIGS)
def test_gen_c(config_file):
    runner = CliRunner()
    output_dir = TEMP_OUTPUT_DIR
    name = "test_output"

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    result = runner.invoke(cli, ["gen-c", config_file, output_dir, "--name", name])
    
    assert result.exit_code == 0
    assert os.path.exists(os.path.join(output_dir, f"{name}.c"))
    assert os.path.exists(os.path.join(output_dir, f"{name}.h"))

    # Clean up generated files
    os.remove(os.path.join(output_dir, f"{name}.c"))
    os.remove(os.path.join(output_dir, f"{name}.h"))
    
def test_gen_c_invalid_input_file():
    runner = CliRunner()
    output_dir = "test/output"
    name = "test_output"
    invalid_config_file = "test/configs/invalid.yaml"

    result = runner.invoke(cli, ["gen-c", invalid_config_file, output_dir, "--name", name])

    assert result.exit_code != 0