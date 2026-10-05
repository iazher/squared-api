import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from squared_api.config import settings

ALGORITHM = "HS256"

password_hasher = PasswordHash.recommended()

# Used when an email doesn't exist, so a failed sign-in takes the same time
# whether or not the account exists (see sign_in in routers/auth.py).
DUMMY_HASH = password_hasher.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: uuid.UUID) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
    return uuid.UUID(payload["sub"])