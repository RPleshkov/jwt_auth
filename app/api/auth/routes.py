import logging
import uuid
from typing import Annotated

from core.redis_client import RedisHelper
from core.security import (
    PAYLOAD_KEY_SUB,
    PAYLOAD_KEY_TOKEN_TYPE,
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_jwt,
    serializer,
    validate_password,
)
from db import repositories
from db.models import User
from db.session import db_helper
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import BadTimeSignature
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.helpers import extract_jti

from .schemas import RegisterResponse, TokenInfo, UserCreate
from .service import get_current_active_auth_user, get_current_token_payload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registry/", status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    in_user: UserCreate,
) -> RegisterResponse:
    try:
        user = await repositories.create_user(
            session=session,
            email=in_user.email,
            password=in_user.password,
        )
        logger.info(
            f"User registered successfully: ID={user.id}, Email={in_user.email}"
        )

        await repositories.save_confirmation_email_to_outbox(
            session=session,
            to_email=in_user.email,
            message_id=str(user.id),
        )

    except IntegrityError:
        logger.warning(f"Attempt to register with existing email: {in_user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user.",
        )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        message="User registered successfully",
    )


@router.post("/token/")
async def login(
    response: Response,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenInfo:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
    email, password = form_data.username, form_data.password
    try:
        logger.info(f"Login attempt for email: {email}")
        user = await repositories.get_user_by_email(session=session, email=email)
        if not user or not validate_password(
            password=password,
            hashed_password=user.password,
        ):
            logger.warning(f"Invalid credentials for email: {email}")
            raise auth_error

        if not user.is_active:
            logger.warning(f"Inactive user attempted to log in: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        logger.info(f"User logged in successfully: {email}")

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        return TokenInfo(access_token=access_token)
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise


@router.post("/token/refresh/")
async def refresh_token(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    refresh_token: str = Cookie(None),
) -> TokenInfo:
    logger.info("Attempting to refresh token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )
    try:
        payload = decode_jwt(refresh_token)
        if payload.get(PAYLOAD_KEY_TOKEN_TYPE) != REFRESH_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user = await repositories.get_user_by_email(
            session=session, email=payload[PAYLOAD_KEY_SUB]
        )
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user",
            )
        access_token = create_access_token(user)
        logger.info(f"Token refreshed successfully for user: {user.email}")
        return TokenInfo(access_token=access_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    token_payload: Annotated[dict, Depends(get_current_token_payload)],
):
    jti = extract_jti(token_payload)
    logger.info(f"Initiating logout for token JTI: {jti}")
    try:
        async with RedisHelper() as redis:
            await redis.add_token_to_blacklist(token_id=jti)  # type: ignore (проверка сделана в get_current_token_payload)
        logger.info(f"Token JTI {jti} successfully added to the blacklist")
    except Exception as e:
        logger.error(f"Failed to add token JTI {jti} to the blacklist: {e}")
        raise HTTPException(status_code=500, detail="Logout failed due to server error")
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    logger.info(f"Refresh token cookie deleted for token JTI: {jti}")
    return None


@router.get("/register_confirm", status_code=status.HTTP_200_OK)
async def confirm_registration(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)], token: str
) -> dict[str, str]:
    try:
        email = serializer.loads(token, max_age=3600)
    except BadTimeSignature:
        raise HTTPException(status_code=400, detail="invalid token")
    try:
        await repositories.confirm_user(session, email)
    except SQLAlchemyError as e:
        logger.error(f"Database error during user confirmation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while confirming the user.",
        )
    return {"message": "Email confirmed successfully", "email": email}


@router.get("/test")
async def test(user: Annotated[User, Depends(get_current_active_auth_user)]):
    return user
