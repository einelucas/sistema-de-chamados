"""Schemas de saida relacionados ao historico de uma solicitacao."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import HistoryAction
from app.schemas.user import UserOut


class RequestHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: HistoryAction
    previous_value: str | None
    new_value: str | None
    user: UserOut
    created_at: datetime
