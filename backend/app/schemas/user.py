"""Schemas de entrada e saida relacionados a usuarios."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole

ThemePreference = Literal["light", "dark"]


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserPasswordReset(BaseModel):
    new_password: str = Field(min_length=6, max_length=100)


class ThemePreferenceUpdate(BaseModel):
    theme_preference: ThemePreference


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    theme_preference: ThemePreference
    created_at: datetime
    updated_at: datetime
