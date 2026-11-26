"""Schemas de entrada e saida relacionados a comentarios."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class CommentCreate(BaseModel):
    public_reply: bool = False
    content: str = Field(min_length=1, max_length=4000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    author: UserOut
    request_id: int
    public_reply: bool
    created_at: datetime
    updated_at: datetime
