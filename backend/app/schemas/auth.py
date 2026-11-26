"""Schemas relacionados a autenticacao."""
from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class ChangePassword(BaseModel):
    current_password:str=Field(min_length=1,max_length=100)
    new_password:str=Field(min_length=12,max_length=72)
