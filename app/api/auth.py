from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from itsdangerous import BadSignature
from sqlalchemy.ext.asyncio import AsyncSession

from services import auth
from database import crud
from database.db import db_helper

router = APIRouter(prefix="/auth")


@router.get("/register_confirm", status_code=status.HTTP_200_OK)
async def confirm_registration(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)], token: str
) -> dict[str, str]:
    try:
        email = auth.serializer.loads(token, max_age=3600)
    except BadSignature:
        raise HTTPException(status_code=400, detail="invalid token")

    await crud.confirm_user(session, email)
    return {"message": "email confirmed"}
