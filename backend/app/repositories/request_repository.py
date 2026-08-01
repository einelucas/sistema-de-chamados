"""Acesso a dados de solicitacoes, incluindo filtros, ordenacao e paginacao."""
from datetime import datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import RequestCategory, RequestPriority, RequestStatus
from app.models.request import Request


class RequestFilters:
    def __init__(
        self,
        search: str | None = None,
        status: RequestStatus | None = None,
        priority: RequestPriority | None = None,
        category: RequestCategory | None = None,
        requester_id: int | None = None,
        assignee_id: int | None = None,
    ) -> None:
        self.search = search
        self.status = status
        self.priority = priority
        self.category = category
        self.requester_id = requester_id
        self.assignee_id = assignee_id


class RequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self) -> Select:
        return (
            select(Request)
            .options(joinedload(Request.requester), joinedload(Request.assignee))
            .where(Request.is_deleted.is_(False))
        )

    def _apply_filters(self, stmt: Select, filters: RequestFilters) -> Select:
        if filters.search:
            like = f"%{filters.search}%"
            stmt = stmt.where(or_(Request.title.ilike(like), Request.description.ilike(like)))
        if filters.status:
            stmt = stmt.where(Request.status == filters.status)
        if filters.priority:
            stmt = stmt.where(Request.priority == filters.priority)
        if filters.category:
            stmt = stmt.where(Request.category == filters.category)
        if filters.requester_id:
            stmt = stmt.where(Request.requester_id == filters.requester_id)
        if filters.assignee_id:
            stmt = stmt.where(Request.assignee_id == filters.assignee_id)
        return stmt

    def list_paginated(
        self,
        filters: RequestFilters,
        skip: int,
        limit: int,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Request], int]:
        stmt = self._apply_filters(self._base_query(), filters)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        sort_columns = {
            "created_at": Request.created_at,
            "priority": Request.priority,
            "status": Request.status,
            "due_date": Request.due_date,
            "title": Request.title,
        }
        column = sort_columns.get(sort_by, Request.created_at)
        order_clause = column.asc() if sort_order == "asc" else column.desc()

        stmt = stmt.order_by(order_clause).offset(skip).limit(limit)
        items = self.db.execute(stmt).unique().scalars().all()
        return list(items), total

    def get_by_id(self, request_id: int) -> Request | None:
        stmt = self._base_query().where(Request.id == request_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def create(self, request: Request) -> Request:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def update(self, request: Request) -> Request:
        self.db.commit()
        self.db.refresh(request)
        return request

    def soft_delete(self, request: Request) -> None:
        request.is_deleted = True
        self.db.commit()

    def count_by_status(self, status: RequestStatus, owner_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(Request).where(
            Request.is_deleted.is_(False), Request.status == status
        )
        stmt = self._scope_to_owner(stmt, owner_id)
        return self.db.execute(stmt).scalar_one()

    def count_overdue(self, now: datetime, owner_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(Request).where(
            Request.is_deleted.is_(False),
            Request.due_date.is_not(None),
            Request.due_date < now,
            Request.status.notin_([RequestStatus.CONCLUIDA, RequestStatus.CANCELADA]),
        )
        stmt = self._scope_to_owner(stmt, owner_id)
        return self.db.execute(stmt).scalar_one()

    def count_total(self, owner_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(Request).where(Request.is_deleted.is_(False))
        stmt = self._scope_to_owner(stmt, owner_id)
        return self.db.execute(stmt).scalar_one()

    def group_count(self, column, owner_id: int | None = None) -> list[tuple]:
        stmt = (
            select(column, func.count())
            .select_from(Request)
            .where(Request.is_deleted.is_(False))
            .group_by(column)
        )
        stmt = self._scope_to_owner(stmt, owner_id)
        return self.db.execute(stmt).all()

    def recent(self, limit: int = 5, owner_id: int | None = None) -> list[Request]:
        stmt = self._base_query().order_by(Request.created_at.desc()).limit(limit)
        stmt = self._scope_to_owner(stmt, owner_id)
        return list(self.db.execute(stmt).unique().scalars().all())

    def all_created_dates(self, owner_id: int | None = None) -> list[datetime]:
        stmt = select(Request.created_at).where(Request.is_deleted.is_(False))
        stmt = self._scope_to_owner(stmt, owner_id)
        return [row[0] for row in self.db.execute(stmt).all()]

    def completed_durations_hours(self, owner_id: int | None = None) -> list[float]:
        stmt = select(Request.created_at, Request.completed_at).where(
            Request.is_deleted.is_(False), Request.completed_at.is_not(None)
        )
        stmt = self._scope_to_owner(stmt, owner_id)
        rows = self.db.execute(stmt).all()
        return [((completed - created).total_seconds() / 3600) for created, completed in rows]

    @staticmethod
    def _scope_to_owner(stmt: Select, owner_id: int | None) -> Select:
        """Restringe a consulta as solicitacoes onde o usuario e solicitante ou responsavel.

        Usado para escopar o dashboard de um perfil USER, que nao deve enxergar indicadores
        globais da empresa, apenas os relacionados as proprias solicitacoes.
        """
        if owner_id is None:
            return stmt
        return stmt.where(or_(Request.requester_id == owner_id, Request.assignee_id == owner_id))
