from typing import Dict, List

import csnake as cc
from odin_python.data_types.custom_enum import EnumeratorDataType
from odin_python.data_types.custom_structure import StructureDataType
from odin_python.parameter.access import (
    AccessConfigurationModel,
    AccessConfigurationType,
    AccessConfigurationTypeFactory,
    AccessConfigurations,
)
from odin_python.parameter.group import ParameterGroupModel
from odin_python.parameter.parameter import ParameterArrayModel, ParameterModel
from odin_python.parameter.store import ParameterStoreModel
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic_yaml import parse_yaml_file_as


class TestReader(BaseModel):
    c_dependencies: List[str] = Field(default_factory=list)

    ram_location: str = "ODIN_ram"

    access_groups: AccessConfigurationType = Field(
        default_factory=AccessConfigurationTypeFactory
    )

    _access_configuration: AccessConfigurations = PrivateAttr()

    extensions: List[str] = Field(default_factory=list)
    types: Dict[str, StructureDataType | EnumeratorDataType] = Field(
        default_factory=dict
    )
    variables: Dict[str, ParameterModel | ParameterArrayModel] = Field(
        default_factory=dict
    )
    datastore: Dict[str, ParameterGroupModel] = Field(default_factory=dict)

    @model_validator(mode="after")
    def populate_names(self):
        for k, v in self.access_groups.items():
            if v is None:
                v = AccessConfigurationModel()
                self.access_groups[k] = v
            v._name = k

        self._access_configuration = AccessConfigurations.inherit(
            self.access_groups, None
        )

        for k, v in self.types.items():
            v._typename = k

        for k, v in self.variables.items():
            v._name = k
            v._parameter_location = None
            v._group_name = None
            v._group_id = None
            v._access_configuration = AccessConfigurations.inherit(
                self._access_configuration, v.access_permissions
            )

        for k, v in self.datastore.items():
            v._name = k
            v._parameter_location = self.ram_location
            v._access_configuration = AccessConfigurations.inherit(
                self._access_configuration, v.access_permissions
            )
            v.apply_naming()

        return self

    @model_validator(mode="after")
    def load_extensions(self):
        for path in self.extensions:
            model = parse_yaml_file_as(TestReader, path)
            self.types.update(model.types)
            self.variables.update(model.variables)
            self.c_dependencies.extend(model.c_dependencies)
        return self

    def generate_simple_file(self, target):
        cw = cc.CodeWriter()
        for k in self.c_dependencies:
            cw.add_line(f"#include <{k}>")

        for k, v in self.types.items():
            objs = v.to_c_typedef()
            if isinstance(objs, cc.Struct):
                cw.add_struct(objs)
            elif isinstance(objs, cc.Enum):
                cw.add_enum(objs)
            # cw.add_variable_declaration(objs)
            cw.add_line("")

        self._access_configuration.create_code(cw)

        datastore = ParameterStoreModel(
            ram_name=self.ram_location,
            parameter_name="odin_params",
            groups=self.datastore,
        )
        cw.add_struct(datastore.to_recursive_typedef(self.types))
        # cw.add_struct(datastore.to_c_typedef(self.types))
        cw.add_struct(datastore.to_recursive_odin_typedef(self.types))
        cw.add_line("")

        cw.add_line("")

        for k, v in self.variables.items():
            cw.add_variable_initialization(v.to_c_initialiser(self.types))
            cw.add_line("")
            cw.add_variable_initialization(
                v.to_c_odin_parameter(self.types, name_prefix="ODIN_")
            )

        # for k, v in self.groups.items():
        #     objs = v.to_c_initialiser(self.types)
        #     cw.add_variable_initialization(objs)
        #     cw.add_line("")

        cw.add_variable_initialization(datastore.to_c_initialiser(self.types))
        cw.add_variable_initialization(
            datastore.to_c_odin_parameter_initialiser(self.types)
        )

        file = str(cw)
        with open(target, "w") as f:
            f.write(file)

    #     cw.add_line("")

    #     opt_gen = AccessOptionsGenerator(config)
    #     # Create opt_gen
    #     opt_gen.add_log_values(cw)

    #     # Add reference definitions
    #     for group in config.datastore.values():
    #         for param in group.data.values():
    #             if param.extension:
    #                 value = param.extension.required_references()
    #                 if value:
    #                     cw.add_line(value)
    #     cw.add_line("")

    #     cw.add_variable_initialization(config.as_variable())
    #     cw.add_line("")

    #     cw.add_variable_initialization(config.as_parameter_store(opt_gen))
    #     cw.add_line("")

    #     for group in config.datastore.values():
    #         cw.add_variable_initialization(group.as_reference())
    #         cw.add_line("")

    #     cw.add_variable_initialization(config.as_reference())
    #     cw.add_line("")

    #     # Generate groups
    #     for group_name, parameters in config.groups.items():
    #         _group = convert_to_virtual_group(config, group_name, parameters)
    #         cw.add_variable_initialization(_group.as_reference())

    #     file = str(cw)
    #     return file

    # with open(target,"w") as f:
    #     f.write("This is a simple file")
    # return target
