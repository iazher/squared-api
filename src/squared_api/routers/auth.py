from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from squared_api.config import settings
from squared_api.dependencies import CurrentUser, SessionDep
from squared_api.models import User
from squared_api.schemas.base import APIModel
from squared_api.schemas.user import UserOut
from squared_api.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class DevSignInRequest(APIModel):
    email: str


class SignInResponse(APIModel):
    access_token: str
    user: UserOut


@router.post("/dev-sign-in", response_model=SignInResponse)
async def dev_sign_in(body: DevSignInRequest, session: SessionDep) -> SignInResponse:
    """Development only: sign in as an existing user by email, no Apple involved."""
    if settings.environment != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with that email")

    return SignInResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def read_me(current_user: CurrentUser) -> User:
    return current_user