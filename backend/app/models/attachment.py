"""Modelo de anexo de uma solicitacao."""
from datetime import datetime

from sqlalchemy import BigInteger, LargeBinary, Boolean, UniqueConstraint, false, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__=(UniqueConstraint("request_id","client_request_id",name="uq_attachment_client_request"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(150), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    shared_with_customer: Mapped[bool] = mapped_column(Boolean,default=False,server_default=false(),nullable=False)
    client_request_id: Mapped[str | None] = mapped_column(String(36),nullable=True)
    file_content: Mapped[bytes | None] = mapped_column(LargeBinary, deferred=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request = relationship("Request", back_populates="attachments")
    uploaded_by = relationship("User")
