import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from squared_api.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(320), unique=True) 
    password_hash: Mapped[str | None] = mapped_column(String(255))
    apple_sub: Mapped[str | None] = mapped_column(String(255), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    venmo_username: Mapped[str | None] = mapped_column(String(100))
    paypal_username: Mapped[str | None] = mapped_column(String(100))
    preferred_currency: Mapped[str] = mapped_column(
        String(3), default="USD", server_default="USD"
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
   
    