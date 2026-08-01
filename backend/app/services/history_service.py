"""Servico responsavel por registrar entradas no historico de uma solicitacao."""
from sqlalchemy.orm import Session

from app.models.enums import HistoryAction
from app.models.history import RequestHistory
from app.repositories.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, db: Session) -> None:
        self.repo = HistoryRepository(db)

    def log(
        self,
        request_id: int,
        user_id: int,
        action: HistoryAction,
        previous_value: str | None = None,
        new_value: str | None = None,
    ) -> RequestHistory:
        entry = RequestHistory(
            request_id=request_id,
            user_id=user_id,
            action=action,
            previous_value=previous_value,
            new_value=new_value,
        )
        return self.repo.create(entry)

    def list_for_request(self, request_id: int) -> list[RequestHistory]:
        return self.repo.list_by_request(request_id)
