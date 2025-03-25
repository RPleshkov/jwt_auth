from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from services import auth
from models.user import User
from schemas.user import CreateUser
from database.db import db_helper

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    in_user: CreateUser,
):
    user = User(
        username=in_user.username,
        password=auth.hash_password(in_user.password),
    )

    session.add(user)
    await session.commit()
    return {"message": "user created successfully"}
