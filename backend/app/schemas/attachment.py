"""Schemas de saida relacionados a anexos."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserOut


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    original_filename: str
    content_type: str
    size_bytes: int
    shared_with_customer: bool
    uploaded_by: UserOut
    created_at: datetime
