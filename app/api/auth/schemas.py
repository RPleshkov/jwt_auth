from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    user_id: UUID
    email: str
    message: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "bearer"
