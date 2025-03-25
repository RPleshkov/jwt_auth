import uuid
from enum import Enum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import Base


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes] = mapped_column(BYTEA)
    email: Mapped[str | None] = mapped_column(String(100), unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(default=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
