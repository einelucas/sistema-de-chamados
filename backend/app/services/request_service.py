"""Regras de negocio de solicitacoes: criacao, atualizacao, transicoes de status, permissoes."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.enums import HistoryAction, RequestStatus, UserRole
from app.models.request import Request
from app.models.user import User
from app.repositories.request_repository import RequestFilters, RequestRepository
from app.schemas.request import (
    RequestAssigneeUpdate,
    RequestCreate,
    RequestPriorityUpdate,
    RequestStatusUpdate,
    RequestUpdate,
)
from app.services.history_service import HistoryService


class RequestService:
    # Transicoes de status permitidas. CONCLUIDA e CANCELADA sao estados terminais: uma
    # solicitacao finalizada so pode ser reaberta explicitamente (ABERTA), nunca pulada
    # diretamente para outro estado intermediario sem revisao.
    ALLOWED_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
        RequestStatus.ABERTA: {RequestStatus.EM_ANDAMENTO, RequestStatus.AGUARDANDO, RequestStatus.CANCELADA},
        RequestStatus.EM_ANDAMENTO: {
            RequestStatus.AGUARDANDO, RequestStatus.CONCLUIDA, RequestStatus.CANCELADA, RequestStatus.ABERTA,
        },
        RequestStatus.AGUARDANDO: {RequestStatus.EM_ANDAMENTO, RequestStatus.CANCELADA, RequestStatus.ABERTA},
        RequestStatus.CONCLUIDA: {RequestStatus.ABERTA},
        RequestStatus.CANCELADA: {RequestStatus.ABERTA},
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RequestRepository(db)
        self.history = HistoryService(db)

    def _can_view(self, request: Request, user: User) -> bool:
        if user.role in (UserRole.ADMIN, UserRole.ANALYST):
            return True
        return request.requester_id == user.id or request.assignee_id == user.id

    def _can_edit(self, request: Request, user: User) -> bool:
        if user.role in (UserRole.ADMIN, UserRole.ANALYST):
            return True
        return request.requester_id == user.id and request.status == RequestStatus.ABERTA

    def list_requests(
        self,
        user: User,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        priority: str | None,
        category: str | None,
        requester_id: int | None,
        assignee_id: int | None,
        sort_by: str,
        sort_order: str,
    ):
        filters = RequestFilters(
            search=search,
            status=status,  # type: ignore[arg-type]
            priority=priority,  # type: ignore[arg-type]
            category=category,  # type: ignore[arg-type]
            requester_id=requester_id,
            assignee_id=assignee_id,
        )
        # Usuario comum so pode ver solicitacoes das quais participa
        if user.role == UserRole.USER:
            filters.requester_id = requester_id or user.id
        skip = (page - 1) * page_size
        items, total = self.repo.list_paginated(filters, skip, page_size, sort_by, sort_order)
        if user.role == UserRole.USER:
            items = [r for r in items if r.requester_id == user.id or r.assignee_id == user.id]
        return items, total

    def get_request(self, request_id: int, user: User) -> Request:
        request = self.repo.get_by_id(request_id)
        if not request:
            raise NotFoundError("Solicitacao nao encontrada")
        if not self._can_view(request, user):
            raise ForbiddenError("Voce nao tem permissao para visualizar esta solicitacao")
        return request

    def create_request(self, payload: RequestCreate, user: User) -> Request:
        request = Request(
            title=payload.title,
            description=payload.description,
            category=payload.category,
            priority=payload.priority,
            due_date=payload.due_date,
            requester_id=user.id,
        )
        request = self.repo.create(request)
        self.history.log(request.id, user.id, HistoryAction.CRIACAO, new_value=request.title)
        return request

    def update_request(self, request_id: int, payload: RequestUpdate, user: User) -> Request:
        request = self.get_request(request_id, user)
        if not self._can_edit(request, user):
            raise ForbiddenError("Voce nao tem permissao para editar esta solicitacao")
        data = payload.model_dump(exclude_unset=True)
        changed_fields = []
        for field, value in data.items():
            if getattr(request, field) != value:
                changed_fields.append(field)
                setattr(request, field, value)
        request = self.repo.update(request)
        if changed_fields:
            self.history.log(
                request.id, user.id, HistoryAction.EDICAO_DADOS, new_value=", ".join(changed_fields)
            )
        return request

    def delete_request(self, request_id: int, user: User) -> None:
        request = self.get_request(request_id, user)
        if user.role != UserRole.ADMIN and request.requester_id != user.id:
            raise ForbiddenError("Voce nao tem permissao para excluir esta solicitacao")
        self.history.log(request.id, user.id, HistoryAction.EXCLUSAO, previous_value=request.status.value)
        self.repo.soft_delete(request)

    def change_status(self, request_id: int, payload: RequestStatusUpdate, user: User) -> Request:
        request = self.get_request(request_id, user)
        if user.role == UserRole.USER:
            raise ForbiddenError("Apenas analistas e administradores podem alterar o status")
        previous = request.status
        if payload.status != previous and payload.status not in self.ALLOWED_TRANSITIONS.get(previous, set()):
            raise AppError(
                f"Transicao de status invalida: nao e possivel ir de {previous.value} para {payload.status.value}."
            )
        request.status = payload.status
        if payload.status == RequestStatus.CONCLUIDA:
            request.completed_at = datetime.now(timezone.utc)
        else:
            request.completed_at = None
        request = self.repo.update(request)
        action = HistoryAction.ALTERACAO_STATUS
        if payload.status == RequestStatus.CONCLUIDA:
            action = HistoryAction.CONCLUSAO
        elif payload.status == RequestStatus.CANCELADA:
            action = HistoryAction.CANCELAMENTO
        self.history.log(request.id, user.id, action, previous_value=previous.value, new_value=payload.status.value)
        return request

    def change_priority(self, request_id: int, payload: RequestPriorityUpdate, user: User) -> Request:
        request = self.get_request(request_id, user)
        if user.role == UserRole.USER:
            raise ForbiddenError("Apenas analistas e administradores podem alterar a prioridade")
        previous = request.priority
        request.priority = payload.priority
        request = self.repo.update(request)
        self.history.log(
            request.id,
            user.id,
            HistoryAction.ALTERACAO_PRIORIDADE,
            previous_value=previous.value,
            new_value=payload.priority.value,
        )
        return request

    def change_assignee(self, request_id: int, payload: RequestAssigneeUpdate, user: User) -> Request:
        request = self.get_request(request_id, user)
        if user.role == UserRole.USER:
            raise ForbiddenError("Apenas analistas e administradores podem atribuir responsavel")
        previous = request.assignee_id
        request.assignee_id = payload.assignee_id
        request = self.repo.update(request)
        self.history.log(
            request.id,
            user.id,
            HistoryAction.MUDANCA_RESPONSAVEL,
            previous_value=str(previous) if previous else None,
            new_value=str(payload.assignee_id) if payload.assignee_id else None,
        )
        return request
