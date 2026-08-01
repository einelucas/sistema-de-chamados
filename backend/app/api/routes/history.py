"""Rota de historico de alteracoes de uma solicitacao."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.history import RequestHistoryOut
from app.services.history_service import HistoryService
from app.services.request_service import RequestService

router = APIRouter(tags=["Historico"])


@router.get(
    "/requests/{request_id}/history", response_model=list[RequestHistoryOut], summary="Lista o historico da solicitacao"
)
def list_history(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Garante que o usuario tem permissao de visualizar a solicitacao antes de exibir o historico
    RequestService(db).get_request(request_id, current_user)
    return HistoryService(db).list_for_request(request_id)
