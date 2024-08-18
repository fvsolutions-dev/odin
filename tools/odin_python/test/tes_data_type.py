from typing import Dict

from odin_python.data_types.custom_structure import StructureDataType
from odin_python.data_types.custom_enum import EnumeratorDataType
from odin_python.parameter.parameter import ParameterModel,ParameterArrayModel
from pydantic import BaseModel, model_validator
from pydantic_yaml import parse_yaml_file_as

TEST_FILE = "test/data_type_test.yaml"


class TestReader(BaseModel):
    types: Dict[str, StructureDataType | EnumeratorDataType]
    variables: Dict[str, ParameterModel|ParameterArrayModel]

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.types.items():
            v._typename = k
            if isinstance(v, StructureDataType):
                v._types = self.types

        for k, v in self.variables.items():
            v._name = k
            v._types = self.types
        return self


model = parse_yaml_file_as(TestReader, TEST_FILE)


for k, v in model.types.items():
    objs = v.to_c_typedef()
    print(objs)
    print()
    # modewl =v.to_model()
    # if modewl:
    #     print(modewl(0))

print("------------------")
for k, v in model.variables.items():
    objs = v.to_c_object()
    print(objs)
    print()
