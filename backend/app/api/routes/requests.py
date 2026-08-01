"""Rotas de gerenciamento de solicitacoes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.enums import RequestCategory, RequestPriority, RequestStatus
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.request import (
    RequestAssigneeUpdate,
    RequestCreate,
    RequestListItem,
    RequestOut,
    RequestPriorityUpdate,
    RequestStatusUpdate,
    RequestUpdate,
)
from app.services.request_service import RequestService
from app.utils.pagination import total_pages

router = APIRouter(prefix="/requests", tags=["Solicitacoes"])


@router.get("", response_model=PaginatedResponse[RequestListItem], summary="Lista solicitacoes com filtros")
def list_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    status: RequestStatus | None = Query(default=None),
    priority: RequestPriority | None = Query(default=None),
    category: RequestCategory | None = Query(default=None),
    requester_id: int | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[RequestListItem]:
    items, total = RequestService(db).list_requests(
        current_user, page, page_size, search, status, priority, category,
        requester_id, assignee_id, sort_by, sort_order,
    )
    return PaginatedResponse(
        items=[RequestListItem.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages(total, page_size),
    )


@router.post("", response_model=RequestOut, status_code=201, summary="Cria uma nova solicitacao")
def create_request(
    payload: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RequestService(db).create_request(payload, current_user)


@router.get("/{request_id}", response_model=RequestOut, summary="Detalha uma solicitacao")
def get_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RequestService(db).get_request(request_id, current_user)


@router.put("/{request_id}", response_model=RequestOut, summary="Atualiza os dados de uma solicitacao")
def update_request(
    request_id: int,
    payload: RequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RequestService(db).update_request(request_id, payload, current_user)


@router.delete("/{request_id}", response_model=MessageResponse, summary="Exclui (logicamente) uma solicitacao")
def delete_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RequestService(db).delete_request(request_id, current_user)
    return MessageResponse(message="Solicitacao removida com sucesso")


@router.patch("/{request_id}/status", response_model=RequestOut, summary="Altera o status da solicitacao")
def change_status(
    request_id: int,
    payload: RequestStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RequestService(db).change_status(request_id, payload, current_user)


@router.patch("/{request_id}/priority", response_model=RequestOut, summary="Altera a prioridade da solicitacao")
def change_priority(
    request_id: int,
    payload: RequestPriorityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RequestService(db).change_priority(request_id, payload, current_user)


@router.patch("/{request_id}/assignee", response_model=RequestOut, summary="Atribui um responsavel a solicitacao")
def change_assignee(
    request_id: int,
    payload: RequestAssigneeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RequestService(db).change_assignee(request_id, payload, current_user)
