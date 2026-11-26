"""Stable tenant/actor mapping for tickets submitted by the Nexotiva gateway."""
from sqlalchemy import ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class NexotivaTicket(Base):
    __tablename__ = "nexotiva_tickets"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", "client_request_id", name="uq_nexotiva_ticket_request"),
        Index("ix_nexotiva_ticket_scope", "company_id", "user_id"),
        Index("ix_nexotiva_ticket_company_module", "company_id", "module_slug"),
    )
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36))
    company_name: Mapped[str] = mapped_column(String(150))
    user_id: Mapped[str] = mapped_column(String(36))
    user_name: Mapped[str] = mapped_column(String(150))
    user_email: Mapped[str] = mapped_column(String(254))
    module_slug: Mapped[str] = mapped_column(String(100))
    module_name: Mapped[str] = mapped_column(String(120))
    client_request_id: Mapped[str] = mapped_column(String(36))

    payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
