from io import StringIO
from pydantic import BaseModel

from .conversion import generate_class
from ..abstract_generator import AbstractGenerator, ModelContext


class PYGenerator(AbstractGenerator):
    class Config(BaseModel):
        pass

    config: BaseModel

    def __init__(self, config: BaseModel):
        super().__init__(config)
        self.config = config

    def generate(self, model_context: ModelContext, output_path: str | StringIO) -> None:
        data = ""
        data += "from odin_python.py_generator.entry import BaseRootModel, ODINBaseEntry, ODINEntry, OdinBool, OdinF32, OdinI32\n\n"
        data += generate_class("RootModel", model_context.root_model, 0)

        data += "\n\n"

        self.save_to_file(output_path, data)
