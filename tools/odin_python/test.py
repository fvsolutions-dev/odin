import enum
from pydantic import BaseModel, field_serializer


class Group(enum.Enum):
    user = 0
    manager = 1
    admin = 2


class User(BaseModel):
    id: int
    username: str
    group: Group | str

    @field_serializer("group")
    def serialize_group(self, group: Group, _info):
        return group.name


user = User(id=1, username="admin", group="admin")

# Serialize the user object
print(user.dict())
