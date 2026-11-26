from datetime import datetime
from sqlalchemy import String,Integer,DateTime,Index
from sqlalchemy.orm import Mapped,mapped_column
from app.database.base import Base
class SupportRevision(Base):
    __tablename__="support_revisions"
    scope:Mapped[str]=mapped_column(String(64),primary_key=True)
    revision:Mapped[str]=mapped_column(String(36),nullable=False)
class SupportOutbox(Base):
    __tablename__="support_outbox"
    __table_args__=(Index("ix_support_outbox_pending","delivered_at","lease_until","created_at"),)
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    company_id:Mapped[str]=mapped_column(String(36))
    user_id:Mapped[str]=mapped_column(String(36))
    ticket_id:Mapped[int]=mapped_column(Integer)
    kind:Mapped[str]=mapped_column(String(30))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
    lease_until:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    delivered_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
