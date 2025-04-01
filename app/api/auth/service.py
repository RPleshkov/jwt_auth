import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from utils.helpers import extract_jti
from core.redis_client import RedisHelper
from db import repositories
from db.models.user import User
from core.security import (
    ACCESS_TOKEN,
    PAYLOAD_KEY_SUB,
    PAYLOAD_KEY_TOKEN_TYPE,
    decode_jwt,
)
from db.session import db_helper

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/")


async def get_current_token_payload(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = decode_jwt(token=token)
        jti = extract_jti(payload)
        async with RedisHelper() as redis:
            if jti is None or (await redis.is_blacklisted_token(jti)):
                raise InvalidTokenError

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error",
        )
    return payload


async def get_current_auth_user(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> User:
    if payload.get(PAYLOAD_KEY_TOKEN_TYPE) != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    email = payload.get(PAYLOAD_KEY_SUB)
    user = await repositories.get_user_by_email(session=session, email=email)  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token (user not found)",
        )
    return user


async def get_current_active_auth_user(
    user: Annotated[User, Depends(get_current_auth_user)],
):
    if user.is_active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
    )
