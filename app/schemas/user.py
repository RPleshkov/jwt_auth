from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str
