"""Modelo de usuario."""
from datetime import datetime

from sqlalchemy import false, Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    integration_identity: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    theme_preference: Mapped[str] = mapped_column(
        String(20), default="light", server_default="light", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    requests_created = relationship(
        "Request", back_populates="requester", foreign_keys="Request.requester_id"
    )
    requests_assigned = relationship(
        "Request", back_populates="assignee", foreign_keys="Request.assignee_id"
    )
    comments = relationship("Comment", back_populates="author")
    history_entries = relationship("RequestHistory", back_populates="user")
