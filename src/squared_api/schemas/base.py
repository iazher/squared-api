import re

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def to_swift_camel(name: str) -> str:
    """paid_by_user_id -> paidByUserID, avatar_url -> avatarURL, member_ids -> memberIDs."""
    camel = to_camel(name)
    camel = re.sub(r"Id(s?)$", r"ID\1", camel)
    return re.sub(r"Url$", "URL", camel)


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_swift_camel,
        populate_by_name=True,
        from_attributes=True,
    )