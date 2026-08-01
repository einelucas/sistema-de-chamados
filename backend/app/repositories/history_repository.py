"""Acesso a dados de historico de solicitacoes."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.history import RequestHistory


class HistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_request(self, request_id: int) -> list[RequestHistory]:
        stmt = (
            select(RequestHistory)
            .options(joinedload(RequestHistory.user))
            .where(RequestHistory.request_id == request_id)
            .order_by(RequestHistory.created_at.desc())
        )
        return list(self.db.execute(stmt).unique().scalars().all())

    def create(self, entry: RequestHistory) -> RequestHistory:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
