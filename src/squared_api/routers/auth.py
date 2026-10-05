from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from squared_api.config import settings
from squared_api.dependencies import CurrentUser, SessionDep
from squared_api.models import User
from squared_api.schemas.auth import (
    DevSignInRequest,
    RegisterRequest,
    SignInRequest,
    SignInResponse,
)
from squared_api.schemas.user import UserOut
from squared_api.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def signed_in(user: User) -> SignInResponse:
    return SignInResponse(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/register", response_model=SignInResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, session: SessionDep) -> SignInResponse:
    email_taken = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="An account with that email already exists",
    )
    if await session.scalar(select(User).where(User.email == body.email)):
        raise email_taken

    user = User(name=body.name, email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        # Someone registered the same email between our check and this insert.
        await session.rollback()
        raise email_taken

    return signed_in(user)


@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(body: SignInRequest, session: SessionDep) -> SignInResponse:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )
    user = await session.scalar(select(User).where(User.email == body.email))

    if user is None or user.password_hash is None:
        verify_password(body.password, DUMMY_HASH)  # same work as a real check, so timing gives nothing away
        raise invalid

    if not verify_password(body.password, user.password_hash):
        raise invalid

    return signed_in(user)


@router.post("/dev-sign-in", response_model=SignInResponse)
async def dev_sign_in(body: DevSignInRequest, session: SessionDep) -> SignInResponse:
    """Development only: sign in as an existing user by email, no password."""
    if settings.environment != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with that email")

    return signed_in(user)


@router.get("/me", response_model=UserOut)
async def read_me(current_user: CurrentUser) -> User:
    return current_user