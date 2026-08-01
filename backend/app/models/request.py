"""Modelo de solicitacao (chamado interno)."""
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import RequestCategory, RequestPriority, RequestStatus


class Request(Base):
    __tablename__ = "requests"
    __table_args__ = (
        Index("ix_requests_status_priority", "status", "priority"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[RequestCategory] = mapped_column(
        Enum(RequestCategory, name="request_category"), nullable=False
    )
    priority: Mapped[RequestPriority] = mapped_column(
        Enum(RequestPriority, name="request_priority"), default=RequestPriority.MEDIA, nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status"), default=RequestStatus.ABERTA, nullable=False
    )

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    requester = relationship("User", back_populates="requests_created", foreign_keys=[requester_id])
    assignee = relationship("User", back_populates="requests_assigned", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="request", cascade="all, delete-orphan")
    history_entries = relationship(
        "RequestHistory", back_populates="request", cascade="all, delete-orphan",
        order_by="RequestHistory.created_at.desc()",
    )
    attachments = relationship("Attachment", back_populates="request", cascade="all, delete-orphan")
