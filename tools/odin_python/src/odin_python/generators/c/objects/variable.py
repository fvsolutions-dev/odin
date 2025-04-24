import csnake as cc

from ....data_types.type_registry import StandardDataType
from ....parameter import (
    ArrayParameterModel,
    BaseBaseParameterModel,
    BaseParameterGroupModel,
    BaseParameterModel,
    ParameterGroupModel,
    ParameterModel,
    RootParameterModel,
    VectorParameterModel,
)
from ....utils.csnake_custom import StructVariable


def to_variable_initialiser(parameter: BaseParameterModel) -> cc.Variable | None:
    if isinstance(parameter, BaseBaseParameterModel):
        # If the reference is set, then we don't need to initialise the variable
        if parameter.reference:
            return None

        if isinstance(parameter, ParameterModel):
            # If the type is void, then we also don't need to initialise the variable
            if parameter.type == "void":
                return None

            assert isinstance(parameter._resolved_type, StandardDataType)

            return parameter._resolved_type.to_c_initialiser(parameter._name, parameter.default)

        elif isinstance(parameter, ArrayParameterModel):
            assert isinstance(parameter._resolved_type, StandardDataType)

            return parameter._resolved_type.to_c_array_initialiser(
                parameter._name,
                parameter.default if parameter.default else [],  # type: ignore
                [parameter.elements],  # type: ignore
            )

        elif isinstance(parameter, VectorParameterModel):
            data = parameter._resolved_type.to_c_array_initialiser(
                parameter._name, parameter.default, [parameter.max_elements]
            )
            length = len(parameter.default) if parameter.default else 0

            return cc.Variable(
                name=parameter._name,
                primitive="UNKNOWN PRIMITIVE",
                value={"data": data.value, "num_elements": length},  # type: ignore
            )

    elif isinstance(parameter, BaseParameterGroupModel):
        if isinstance(parameter, RootParameterModel):
            assert parameter._c_types is not None, "C types are not set"
            name = parameter._c_types.variables_name
            type = parameter._c_types.variables_type
        else:
            name = parameter._name
            type = "UNKNOWN PRIMITIVE"

        values = {}
        for child in parameter.children.values():
            initialiser = to_variable_initialiser(child)

            if initialiser:
                values[initialiser.name] = initialiser.value

        if len(values) == 0:
            return None

        return cc.Variable(name=name, primitive=type, value=values)  # type: ignore


def to_variable_type(parameter: BaseParameterModel, type_name: str | None = None) -> cc.Struct | None:
    if isinstance(parameter, VectorParameterModel):
        if type_name:
            struct = StructVariable(name=type_name, typedef=True)
        else:
            struct = StructVariable(var_name=parameter._name, typedef=False)

        struct.add_variable(
            cc.Variable(
                name="num_elements",
                primitive="size_t",
                value=len(parameter.default) if parameter.default else 0,  # type: ignore
            ),
        )

        struct.add_variable(
            parameter._resolved_type.to_c_array_initialiser("data", parameter.default, [parameter.max_elements])
        )
        return struct

    elif isinstance(parameter, BaseParameterGroupModel):
        if isinstance(parameter, RootParameterModel):
            assert parameter._c_types is not None, "C types are not set"
            struct = StructVariable(name=parameter._c_types.variables_type, typedef=True)
        else:
            struct = StructVariable(var_name=parameter._name, typedef=False)

        items = 0

        for child in parameter.children.values():
            if isinstance(child, ParameterGroupModel):
                variable_type = to_variable_type(child)
                if variable_type:
                    struct.add_struct(variable_type)
                    items += 1

            elif isinstance(child, VectorParameterModel):
                to_variable_initialiser(child)
                variable_type = to_variable_type(child)
                if variable_type:
                    struct.add_struct(variable_type)
                    items += 1

            elif isinstance(child, ParameterModel) or isinstance(child, ArrayParameterModel):
                variable = to_variable_initialiser(child)
                if variable:
                    struct.add_variable(variable)
                    items += 1

            else:
                raise ValueError("Unknown type")

        if items == 0:
            return None

        return struct

    else:
        raise ValueError("Unknown type")
