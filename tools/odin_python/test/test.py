from odin_python.main_model import TestReader
from pydantic_yaml import parse_yaml_file_as
import os
from odin_python.c_generator import CGenerator

FILES = [
    "test/configs/single_variables.yaml",
    "test/configs/array_variables.yaml",
    "test/configs/group_variables.yaml",
    "test/configs/muov/datastore_config_minimal.yaml",
    "test/configs/permissions.yaml",
    "/root/dev/tilt-bike/boards/comms-esp/main/app_datastore/datastore_config.yaml",
    "test/configs/referenced.yaml"
]
for file in FILES:
    try:
        model = TestReader.from_yaml(file)
        file_name = file.split("/")[-1].split(".")[0]

        OUTPUT_DIR = "test/output"
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        generator = CGenerator(OUTPUT_DIR, file_name, model)
        generator.generate_header()
        generator.generate_source()

        INCLUDE_DIR = "../.."
        # # Test compulation as lib
        os.system(
            f"gcc -c {generator.source_filepath} -I {INCLUDE_DIR}  -I {OUTPUT_DIR}  -o {OUTPUT_DIR}/{file_name}.o"
        )
    except Exception as e:
        print(f"Error in file {file}")
        
        print(e)
        
    # Get size of the the ram
    