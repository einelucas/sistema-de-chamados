"""Regras de negocio de autenticacao."""
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, AppError
from app.core.security import hash_password
from app.services.bootstrap import bootstrap_admin
from app.core.config import settings
from sqlalchemy import select
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def login(self, payload: LoginRequest) -> TokenResponse:
        if settings.BOOTSTRAP_ADMIN and payload.email.lower()==settings.ADMIN_EMAIL.lower():
            bootstrap_admin(self.db)
        user = self.users.get_by_email(payload.email.lower())
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("E-mail ou senha invalidos")
        if not user.is_active or user.integration_identity or user.email.lower().endswith('@integration.example.com'):
            raise UnauthorizedError("Usuario inativo. Contate o administrador.")

        token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value,"sv":user.session_version})
        return TokenResponse(access_token=token, user=user)  # type: ignore[arg-type]

    def get_current_user_from_sub(self, user_id: int) -> User | None:
        return self.users.get_by_id(user_id)

    def change_password(self,user,payload):
        user=self.db.scalar(select(User).where(User.id==user.id).with_for_update().execution_options(populate_existing=True))
        if not user or not verify_password(payload.current_password,user.hashed_password):
            raise UnauthorizedError("Senha atual inválida")
        if len(payload.new_password.encode("utf-8"))>72 or verify_password(payload.new_password,user.hashed_password):
            raise AppError("Escolha uma senha diferente, de 12 a 72 bytes")
        user.hashed_password=hash_password(payload.new_password)
        user.must_change_password=False
        user.session_version+=1
        self.db.commit()
        self.db.refresh(user)
        token=create_access_token(str(user.id),{"role":user.role.value,"sv":user.session_version})
        return TokenResponse(access_token=token,user=user)
