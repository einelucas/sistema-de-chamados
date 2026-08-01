"""Regras de negocio de comentarios em solicitacoes."""
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.comment import Comment
from app.models.enums import HistoryAction, UserRole
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.request_repository import RequestRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.history_service import HistoryService


class CommentService:
    def __init__(self, db: Session) -> None:
        self.repo = CommentRepository(db)
        self.requests = RequestRepository(db)
        self.history = HistoryService(db)

    def _ensure_request_exists(self, request_id: int) -> None:
        if not self.requests.get_by_id(request_id):
            raise NotFoundError("Solicitacao nao encontrada")

    def list_comments(self, request_id: int) -> list[Comment]:
        self._ensure_request_exists(request_id)
        return self.repo.list_by_request(request_id)

    def create_comment(self, request_id: int, payload: CommentCreate, user: User) -> Comment:
        self._ensure_request_exists(request_id)
        comment = Comment(content=payload.content, author_id=user.id, request_id=request_id)
        comment = self.repo.create(comment)
        self.history.log(request_id, user.id, HistoryAction.COMENTARIO_ADICIONADO)
        return comment

    def _get_owned_comment(self, comment_id: int, user: User) -> Comment:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comentario nao encontrado")
        if comment.author_id != user.id and user.role != UserRole.ADMIN:
            raise ForbiddenError("Voce so pode alterar seus proprios comentarios")
        return comment

    def update_comment(self, comment_id: int, payload: CommentUpdate, user: User) -> Comment:
        comment = self._get_owned_comment(comment_id, user)
        comment.content = payload.content
        return self.repo.update(comment)

    def delete_comment(self, comment_id: int, user: User) -> None:
        comment = self._get_owned_comment(comment_id, user)
        self.repo.delete(comment)
