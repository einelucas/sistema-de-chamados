"""Acesso a dados de comentarios."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_request(self, request_id: int) -> list[Comment]:
        stmt = (
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.request_id == request_id)
            .order_by(Comment.created_at.asc())
        )
        return list(self.db.execute(stmt).unique().scalars().all())

    def get_by_id(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).options(joinedload(Comment.author)).where(Comment.id == comment_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()
