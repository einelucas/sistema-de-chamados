"""Schemas de entrada e saida relacionados a solicitacoes."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RequestCategory, RequestPriority, RequestStatus
from app.schemas.user import UserOut


class RequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    category: RequestCategory
    priority: RequestPriority = RequestPriority.MEDIA
    due_date: datetime | None = None


class RequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=3)
    category: RequestCategory | None = None
    due_date: datetime | None = None


class RequestStatusUpdate(BaseModel):
    status: RequestStatus


class RequestPriorityUpdate(BaseModel):
    priority: RequestPriority


class RequestAssigneeUpdate(BaseModel):
    assignee_id: int | None = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: RequestCategory
    priority: RequestPriority
    status: RequestStatus
    requester: UserOut
    assignee: UserOut | None
    due_date: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RequestListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: RequestCategory
    priority: RequestPriority
    status: RequestStatus
    requester: UserOut
    assignee: UserOut | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
