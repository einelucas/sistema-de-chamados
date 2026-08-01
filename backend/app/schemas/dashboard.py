"""Schemas de saida do dashboard consolidado."""
from datetime import datetime

from pydantic import BaseModel

from app.schemas.request import RequestListItem


class CountByLabel(BaseModel):
    label: str
    total: int


class PeriodCount(BaseModel):
    period: str
    total: int


class DashboardSummary(BaseModel):
    total_requests: int
    open_requests: int
    in_progress_requests: int
    completed_requests: int
    overdue_requests: int
    by_priority: list[CountByLabel]
    by_status: list[CountByLabel]
    by_category: list[CountByLabel]
    created_by_period: list[PeriodCount]
    average_completion_hours: float | None
    recent_requests: list[RequestListItem]
    generated_at: datetime
