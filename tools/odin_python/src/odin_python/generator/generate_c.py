import csnake as cc

from odin_python.parameter.parameter import (
    RootParameterModel,
)


class CGenerator:
    STORE_TYPE = "root_type_t"
    STORE_NAME = "root"

    RAM_TYPE = "root_ram_t"
    RAM_NAME = "root_ram"

    @staticmethod
    def generate_source(model: RootParameterModel):
        cw = cc.CodeWriter()
        # Generate the ram storage type
        cw.add_variable_initialization(
            model.to_c_initialiser(CGenerator.RAM_NAME, CGenerator.RAM_TYPE)
        )
        cw.add_line("")

        cw.add_variable_initialization(
            model.to_c_odin_parameter_initialiser(
                param_name=CGenerator.STORE_NAME, type_name=CGenerator.STORE_TYPE
            )
        )
        cw.add_line("")

        return str(cw)

    @staticmethod
    def generate_header(model: RootParameterModel):
        cw = cc.CodeWriter()
        cw.add_line("#include <stdint.h>")
        cw.add_line("#include <stdbool.h>")
        cw.add_line("#include <odin.h>")
        cw.add_line("")

        cw.add_struct(model.to_ram_struct(CGenerator.RAM_TYPE))
        cw.add_line("")

        cw.add_struct(model.to_recursive_odin_typedef(type_name=CGenerator.STORE_TYPE))
        cw.add_line("")

        return str(cw)

    @staticmethod
    def generate_single_source(model: RootParameterModel):
        return (
            CGenerator.generate_header(model) + "\n" + CGenerator.generate_source(model)
        )


# class CGenerator:
#     def __init__(
#         self,
#         ouput_dir: str,
#         file_name: str,
#         model: RootParameterModel,
#     ):
#         self.output_dir = ouput_dir
#         self.file_name = file_name

#         self.model = model

#     @property
#     def header_filepath(self):
#         return os.path.join(self.output_dir, f"{self.file_name}.h")

#     @property
#     def source_filepath(self):
#         return os.path.join(self.output_dir, f"{self.file_name}.c")

#     # def generate_header(self):
#     # cw = cc.CodeWriter()

#     #     # Generate ram storage type
#     #     cw.add_struct(self.model._datastore.ram_typedef(self.model.types))
#     #     cw.add_line("")

#     #     # # Generate parameter storage type
#     #     cw.add_struct(self.model._datastore.to_recursive_odin_typedef(self.model.types))
#     #     cw.add_line("")

#     #     # #TODO add external variables

#     #     with open(self.header_filepath, "w") as f:
#     #         f.write(str(cw))

#     def generate_source(self):
#         cw = cc.CodeWriter()
#         cw.add_line(f"#include <{self.file_name}.h>")
#         cw.add_line("")

#         # cw.add_variable_initialization(
#         #     self.model._datastore.to_c_initialiser(self.model.types)
#         # )

#         # cw.add_variable_initialization(
#         #     self.model._datastore.to_c_odin_parameter_initialiser(self.model.types)
#         # )

#         # cw.add_variable_initialization(
#         #     self.model._datastore.to_tree_definition(self.model.types)
#         # )
#         cw.add_line("")
#         cw.add_struct(to_recursive_odin_typedef(model.root))
#         cw.add_line("")
#         cw.add_variable_initialization(model.to_c_odin_parameter_initialiser())

#         # Generate groups
#         # for group in self.model.parameters.values():
#         #     cw.add_variable_initialization(
#         #         group.to_c_odin_group(self.model.config.parameter_name)
#         #     )
#         #     cw.add_line("")

#         file = str(cw)
#         with open(self.source_filepath, "w") as f:
#             f.write(file)
