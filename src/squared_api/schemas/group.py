import uuid
from typing import Annotated

from pydantic import Field, StringConstraints

from squared_api.schemas.base import APIDateTime, APIModel

GroupName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class GroupOut(APIModel):
    id: uuid.UUID
    name: str
    member_ids: list[uuid.UUID]
    created_at: APIDateTime


class GroupCreate(APIModel):
    name: GroupName
    member_ids: list[uuid.UUID] = Field(default_factory=list)