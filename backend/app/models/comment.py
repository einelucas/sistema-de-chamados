"""Modelo de comentario em uma solicitacao."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, String, Boolean, UniqueConstraint, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (UniqueConstraint("request_id","client_request_id",name="uq_comment_client_request"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    public_reply: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    client_request_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author = relationship("User", back_populates="comments")
    request = relationship("Request", back_populates="comments")
