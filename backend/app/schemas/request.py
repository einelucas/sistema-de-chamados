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


class NexotivaMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    company_id: str
    company_name: str
    user_name: str
    user_email: str
    module_slug: str
    module_name: str

class RequestUpdate(BaseModel):
    expected_version: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=3)
    category: RequestCategory | None = None
    due_date: datetime | None = None


class RequestStatusUpdate(BaseModel):
    expected_version: int | None = Field(default=None, ge=1)
    status: RequestStatus


class RequestPriorityUpdate(BaseModel):
    expected_version: int | None = Field(default=None, ge=1)
    priority: RequestPriority


class RequestAssigneeUpdate(BaseModel):
    expected_version: int | None = Field(default=None, ge=1)
    assignee_id: int | None = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: int
    nexotiva: NexotivaMetadata | None = None
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
    version: int
    nexotiva: NexotivaMetadata | None = None
    title: str
    category: RequestCategory
    priority: RequestPriority
    status: RequestStatus
    requester: UserOut
    assignee: UserOut | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
