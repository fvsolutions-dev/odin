import csnake as cc

from ....generators.c.model import ODIN_ParameterGroupModel
from ....parameter import (
    BaseParameterGroupModel,
    ParameterGroupModel,
)


def to_group_initialiser(self: BaseParameterGroupModel) -> list[cc.Variable]:
    variables = []

    # Create the data structures for this group
    parameters_references = []
    for parameter in self.children.values():
        if isinstance(parameter, BaseParameterGroupModel):
            parameters_references.append(parameter.absolute_group_reference)
        else:
            parameters_references.append(parameter.absolute_object_reference)

    variables.append(
        ODIN_ParameterGroupModel(
            param_name=self.absolute_group_reference,
            name=self._name,
            description=self.resolved_description,
            global_id=self.global_id,
            id_space_shift=self.id_space_shift,
            parameters_references=parameters_references,
        ).variable
    )

    # Create the data structures for the children
    for parameter in self.children.values():
        if isinstance(parameter, ParameterGroupModel):
            variables.extend(to_group_initialiser(parameter))

    return variables
