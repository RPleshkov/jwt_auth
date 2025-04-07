from typing import Any

from core.security import hash_password
from db.models.outbox import Outbox
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    user = User(
        email=email,
        password=hash_password(password),
    )
    session.add(user)
    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()


async def save_confirmation_email_to_outbox(
    session: AsyncSession,
    to_email: str,
    message_id: str,
) -> None:
    payload = {
        "to_email": to_email,
        "message_id": message_id,
    }
    message = Outbox(payload=payload)
    session.add(message)
    await session.commit()


async def confirm_user(session: AsyncSession, email: str) -> None:
    stmt = (
        update(User)
        .where(User.email == email)
        .values(
            is_verified=True,
        )
    )
    await session.execute(stmt)
    await session.commit()
