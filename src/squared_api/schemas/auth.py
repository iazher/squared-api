from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints, field_validator

from squared_api.schemas.base import APIModel
from squared_api.schemas.user import UserOut

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class RegisterRequest(APIModel):
    name: Name
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class SignInRequest(APIModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class DevSignInRequest(APIModel):
    email: str


class SignInResponse(APIModel):
    access_token: str
    user: UserOut