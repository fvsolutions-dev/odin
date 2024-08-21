import os

import csnake as cc
from urllib3 import Retry

from .main_model import TestReader


class CGenerator:
    def __init__(self, ouput_dir: str, file_name: str, model: TestReader):
        self.output_dir = ouput_dir
        self.file_name = file_name

        self.model = model

    @property
    def header_filepath(self):
        return os.path.join(self.output_dir, f"{self.file_name}.h")

    @property
    def source_filepath(self):
        return os.path.join(self.output_dir, f"{self.file_name}.c")

    def generate_header(self):
        cw = cc.CodeWriter()

        # Add includes
        for k in self.model.includes:
            cw.add_line(f"#include <{k}>")

        cw.add_line("")

        # Geneatae acces macros
        self.model._access_configuration.create_code(cw)

        cw.add_line("")

        # Add types
        for type in self.model.types.values():
            obj = type.to_c_typedef()

            if isinstance(obj, cc.Struct):
                cw.add_struct(obj)
            elif isinstance(obj, cc.Enum):
                cw.add_enum(obj)

            cw.add_line("")

        # Generate ram storage type
        cw.add_struct(self.model._datastore.ram_typedef(self.model.types))
        cw.add_line("")

        # # Generate parameter storage type
        cw.add_struct(self.model._datastore.to_recursive_odin_typedef(self.model.types))
        cw.add_line("")

        # #TODO add external variables

        with open(self.header_filepath, "w") as f:
            f.write(str(cw))

    def generate_source(self):
        cw = cc.CodeWriter()
        cw.add_line(f"#include <{self.file_name}.h>")
        cw.add_line("")


        cw.add_variable_initialization(self.model._datastore.to_c_initialiser(self.model.types))
        
        cw.add_variable_initialization(
            self.model._datastore.to_c_odin_parameter_initialiser(self.model.types)
        )

        cw.add_variable_initialization(
            self.model._datastore.to_tree_definition(self.model.types)
        )
        # Generate groups
        # for group in self.model.parameters.values():
        #     cw.add_variable_initialization(
        #         group.to_c_odin_group(self.model.config.parameter_name)
        #     )
        #     cw.add_line("")

        file = str(cw)
        with open(self.source_filepath, "w") as f:
            f.write(file)
