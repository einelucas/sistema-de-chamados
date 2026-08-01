"""Servico que consolida os indicadores do dashboard a partir do backend.

Para os perfis ADMIN e ANALYST, os indicadores sao globais (toda a empresa). Para o perfil
USER, os indicadores sao restritos as solicitacoes onde o usuario e solicitante ou
responsavel -- um usuario comum nao deve enxergar totais agregados de outras pessoas.
"""
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import RequestStatus, UserRole
from app.models.request import Request
from app.models.user import User
from app.repositories.request_repository import RequestRepository
from app.schemas.dashboard import CountByLabel, DashboardSummary, PeriodCount
from app.schemas.request import RequestListItem


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.repo = RequestRepository(db)

    def get_summary(self, user: User) -> DashboardSummary:
        owner_id = None if user.role in (UserRole.ADMIN, UserRole.ANALYST) else user.id

        now = datetime.now(timezone.utc)
        total = self.repo.count_total(owner_id)
        open_count = self.repo.count_by_status(RequestStatus.ABERTA, owner_id)
        in_progress = self.repo.count_by_status(RequestStatus.EM_ANDAMENTO, owner_id)
        completed = self.repo.count_by_status(RequestStatus.CONCLUIDA, owner_id)
        overdue = self.repo.count_overdue(now, owner_id)

        by_priority = [
            CountByLabel(label=self._label(k), total=v)
            for k, v in self.repo.group_count(Request.priority, owner_id)
        ]
        by_status = [
            CountByLabel(label=self._label(k), total=v)
            for k, v in self.repo.group_count(Request.status, owner_id)
        ]
        by_category = [
            CountByLabel(label=self._label(k), total=v)
            for k, v in self.repo.group_count(Request.category, owner_id)
        ]

        durations = self.repo.completed_durations_hours(owner_id)
        average_hours = round(sum(durations) / len(durations), 2) if durations else None

        recent = self.repo.recent(limit=5, owner_id=owner_id)
        created_by_period = self._group_by_month(self.repo.all_created_dates(owner_id))

        return DashboardSummary(
            total_requests=total,
            open_requests=open_count,
            in_progress_requests=in_progress,
            completed_requests=completed,
            overdue_requests=overdue,
            by_priority=by_priority,
            by_status=by_status,
            by_category=by_category,
            created_by_period=created_by_period,
            average_completion_hours=average_hours,
            recent_requests=[RequestListItem.model_validate(r) for r in recent],
            generated_at=now,
        )

    @staticmethod
    def _label(value) -> str:
        return value.value if hasattr(value, "value") else str(value)

    @staticmethod
    def _group_by_month(dates: list[datetime]) -> list[PeriodCount]:
        counts: dict[str, int] = defaultdict(int)
        for created in dates:
            counts[created.strftime("%Y-%m")] += 1
        ordered_keys = sorted(counts.keys())[-12:]
        return [PeriodCount(period=key, total=counts[key]) for key in ordered_keys]
