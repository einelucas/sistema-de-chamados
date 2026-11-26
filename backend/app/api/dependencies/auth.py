"""Dependencias de autenticacao e controle de acesso por papel."""
from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Token de acesso ausente")

    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Token invalido ou expirado")

    user = UserRepository(db).get_by_id(int(payload["sub"]))
    if not user:
        raise UnauthorizedError("Usuario nao encontrado")
    if not user.is_active or user.integration_identity or user.email.lower().endswith('@integration.example.com'):
        raise UnauthorizedError("Usuario inativo")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("Voce nao tem permissao para executar esta acao")
        return current_user

    return dependency


require_admin = require_roles(UserRole.ADMIN)
require_analyst_or_admin = require_roles(UserRole.ADMIN, UserRole.ANALYST)
