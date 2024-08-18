from parser import TestReader
from pydantic_yaml import parse_yaml_file_as
import os

FILES = ["test/configs/single_variables.yaml", "test/configs/array_variables.yaml"]
for file in FILES:
    model = parse_yaml_file_as(TestReader, file)
    file_name = file.split("/")[-1].split(".")[0]

    output_file = f"test/output/{file_name}.c"
    os.makedirs("test/output", exist_ok=True)
    model.generate_simple_file(output_file)

    # Test compulation as lib
    os.system(f"gcc -c {output_file} -o test/output/{file_name}.o")