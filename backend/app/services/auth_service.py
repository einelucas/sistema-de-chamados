"""Regras de negocio de autenticacao."""
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("E-mail ou senha invalidos")
        if not user.is_active or user.integration_identity or user.email.lower().endswith('@integration.example.com'):
            raise UnauthorizedError("Usuario inativo. Contate o administrador.")

        token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
        return TokenResponse(access_token=token, user=user)  # type: ignore[arg-type]

    def get_current_user_from_sub(self, user_id: int) -> User | None:
        return self.users.get_by_id(user_id)
