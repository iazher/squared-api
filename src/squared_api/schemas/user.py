import uuid

from squared_api.schemas.base import APIModel


class UserOut(APIModel):
    id: uuid.UUID
    name: str
    email: str | None
    avatar_url: str | None
    venmo_username: str | None
    paypal_username: str | None