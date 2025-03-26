from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import CreateUser
from services import auth


async def create_user(session: AsyncSession, in_user: CreateUser):
    user = User(
        email=in_user.email,
        password=auth.hash_password(in_user.password),
    )
    session.add(user)
    await session.commit()


async def confirm_user(session: AsyncSession, email: str):
    stmt = (
        update(User)
        .where(User.email == email)
        .values(
            is_verified=True,
            is_active=True,
        )
    )
    await session.execute(stmt)
    await session.commit()
