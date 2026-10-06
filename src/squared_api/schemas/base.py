import re
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel


def to_swift_camel(name: str) -> str:
    """paid_by_user_id -> paidByUserID, avatar_url -> avatarURL, member_ids -> memberIDs."""
    camel = to_camel(name)
    camel = re.sub(r"Id(s?)$", r"ID\1", camel)
    return re.sub(r"Url$", "URL", camel)


def to_swift_date(value: datetime) -> str:
    """2026-10-06T13:15:00Z: UTC, whole seconds. Swift's .iso8601 decoder rejects fractional seconds."""
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


APIDateTime = Annotated[datetime, PlainSerializer(to_swift_date, return_type=str, when_used="json")]


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_swift_camel,
        populate_by_name=True,
        from_attributes=True,
    )