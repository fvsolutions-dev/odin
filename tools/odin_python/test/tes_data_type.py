from typing import Dict

from odin_python.data_types.data_types import EnumDataType, StructDataType
from odin_python.data_types.parameter import ParameterModel
from pydantic import BaseModel, model_validator
from pydantic_yaml import parse_yaml_file_as

TEST_FILE = "test/data_type_test.yaml"


class TestReader(BaseModel):
    types: Dict[str, StructDataType | EnumDataType]
    variables: Dict[str, ParameterModel]

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.types.items():
            v._name = k

        for k, v in self.variables.items():
            v._name = k
            v._types = self.types
        return self


model = parse_yaml_file_as(TestReader, TEST_FILE)


for k, v in model.types.items():
    objs = v.to_c_object()
    print(objs)
    # modewl =v.to_model()
    # if modewl:
    #     print(modewl(0))    


for k, v in model.variables.items():
    objs = v.to_c_object()
    print(objs)