import uuid
from enum import Enum
from typing import Any

from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Status(str, Enum):
    sent = "sent"
    pending = "pending"
    failed = "failed"


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[Status] = mapped_column(default=Status.pending)
