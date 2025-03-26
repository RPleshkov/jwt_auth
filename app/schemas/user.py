from pydantic import BaseModel, EmailStr, Field


class CreateUser(BaseModel):
    email: EmailStr = Field(min_length=3, max_length=70)
    password: str
