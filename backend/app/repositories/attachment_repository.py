"""Acesso a dados de anexos."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_request(self, request_id: int) -> list[Attachment]:
        stmt = (
            select(Attachment)
            .options(joinedload(Attachment.uploaded_by))
            .where(Attachment.request_id == request_id)
            .order_by(Attachment.created_at.desc())
        )
        return list(self.db.execute(stmt).unique().scalars().all())

    def get_by_id(self, attachment_id: int) -> Attachment | None:
        stmt = select(Attachment).options(joinedload(Attachment.uploaded_by)).where(Attachment.id == attachment_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def create(self, attachment: Attachment) -> Attachment:
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def delete(self, attachment: Attachment) -> None:
        self.db.delete(attachment)
        self.db.commit()
