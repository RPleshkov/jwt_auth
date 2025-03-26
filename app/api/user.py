from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import CreateUser
from database.db import db_helper
from mail.tasks import send_confirmation_email
from database import crud
from services import auth

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    in_user: CreateUser,
):
    try:
        await crud.create_user(session, in_user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="such a user already exists"
        )
    confirmation_token = auth.serializer.dumps(in_user.email)
    send_confirmation_email.delay(to_email=in_user.email, token=confirmation_token)
    return {"message": "user created successfully"}
