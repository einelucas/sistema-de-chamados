"""Regras de negocio de usuarios (area administrativa).

Alem do CRUD basico, este servico centraliza duas protecoes de seguranca importantes:
- Nenhuma acao pode remover, desativar ou rebaixar o ULTIMO administrador ativo do sistema,
  o que deixaria o sistema sem ninguem capaz de gerenciar usuarios.
- Um administrador nao pode remover ou desativar a propria conta (autoexclusao), evitando
  bloqueios acidentais de acesso.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import ThemePreferenceUpdate, UserCreate, UserPasswordReset, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def list_users(self, page: int, page_size: int) -> tuple[list[User], int]:
        skip = (page - 1) * page_size
        return self.repo.list_all(skip=skip, limit=page_size)

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuario nao encontrado")
        return user

    def create_user(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email):
            raise ConflictError("Ja existe um usuario com este e-mail")
        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        return self.repo.create(user)

    def _ensure_not_last_admin(self, user: User, acting_user: User, action: str) -> None:
        """Impede desativar/rebaixar/excluir o ultimo administrador ativo do sistema."""
        if user.role != UserRole.ADMIN or not user.is_active:
            return
        remaining_admins = self.repo.count_active_admins(exclude_user_id=user.id)
        if remaining_admins == 0:
            raise ConflictError(
                f"Nao e possivel {action}: este e o ultimo administrador ativo do sistema."
            )

    def update_user(self, user_id: int, payload: UserUpdate, acting_user: User) -> User:
        user = self.get_user(user_id)
        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"] != user.email:
            if self.repo.get_by_email(data["email"]):
                raise ConflictError("Ja existe um usuario com este e-mail")

        if "role" in data and data["role"] != user.role and user.role == UserRole.ADMIN:
            self._ensure_not_last_admin(user, acting_user, "alterar o papel deste usuario")
            if user.id == acting_user.id:
                raise ForbiddenError(
                    "Voce nao pode alterar o proprio papel de administrador. "
                    "Peca a outro administrador para realizar esta alteracao."
                )

        if "is_active" in data and data["is_active"] is False:
            if user.id == acting_user.id:
                raise ForbiddenError("Voce nao pode desativar a propria conta.")
            self._ensure_not_last_admin(user, acting_user, "desativar este usuario")

        for field, value in data.items():
            setattr(user, field, value)
        return self.repo.update(user)

    def update_theme_preference(
        self, user: User, payload: ThemePreferenceUpdate
    ) -> User:
        """Atualiza somente a preferencia visual do proprio usuario autenticado."""
        user.theme_preference = payload.theme_preference
        return self.repo.update(user)

    def reset_password(self, user_id: int, payload: UserPasswordReset) -> User:
        user = self.get_user(user_id)
        user.hashed_password = hash_password(payload.new_password)
        return self.repo.update(user)

    def set_active(self, user_id: int, is_active: bool, acting_user: User) -> User:
        user = self.get_user(user_id)
        if not is_active:
            if user.id == acting_user.id:
                raise ForbiddenError("Voce nao pode desativar a propria conta.")
            self._ensure_not_last_admin(user, acting_user, "desativar este usuario")
        user.is_active = is_active
        return self.repo.update(user)

    def delete_user(self, user_id: int, acting_user: User) -> None:
        user = self.get_user(user_id)
        if user.id == acting_user.id:
            raise ForbiddenError("Voce nao pode excluir a propria conta.")
        self._ensure_not_last_admin(user, acting_user, "excluir este usuario")
        try:
            self.repo.delete(user)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(
                "Nao e possivel excluir este usuario: existem solicitacoes, comentarios, "
                "anexos ou historico vinculados a ele. Desative o usuario em vez de exclui-lo."
            )
