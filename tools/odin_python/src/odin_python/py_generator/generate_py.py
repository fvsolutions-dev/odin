from turtle import reset
import csnake as cc

from odin_python.parameter import (
    RootParameterModel,
)
from odin_python.parameter.parameter import C_Names


class CGenerator:
    # TYPES = C_Names(
    #     objects_name="odin_objects",
    #     objects_type="odin_objects_t",
    #     variables_name="odin_variables",
    #     variables_type="odin_variables_t",
    #     groups_name="odin_store",
    # )

    @staticmethod
    def generate_lib(model: RootParameterModel) -> str:
        return model.dump_json()

    
    @staticmethod
    def generate_single_source(
        model: RootParameterModel
    ) -> str:
        return (
            CGenerator.generate_lib(model)
        )
