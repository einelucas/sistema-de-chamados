"""Agrega todos os modelos para que o Alembic e o SQLAlchemy os enxerguem."""
from app.models.attachment import Attachment
from app.models.comment import Comment
from app.models.history import RequestHistory
from app.models.request import Request
from app.models.user import User

__all__ = ["User", "Request", "Comment", "RequestHistory", "Attachment"]
