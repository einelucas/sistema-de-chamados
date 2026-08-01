"""Rotas de gerenciamento de usuarios (area administrativa, com leitura liberada a analistas)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_admin, require_analyst_or_admin
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import (
    ThemePreferenceUpdate,
    UserCreate,
    UserOut,
    UserPasswordReset,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.pagination import total_pages

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "",
    response_model=PaginatedResponse[UserOut],
    summary="Lista usuarios (admin e analistas, para atribuicao de responsaveis)",
    dependencies=[Depends(require_analyst_or_admin)],
)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> PaginatedResponse[UserOut]:
    items, total = UserService(db).list_users(page, page_size)
    return PaginatedResponse(
        items=[UserOut.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages(total, page_size),
    )


@router.post(
    "", response_model=UserOut, status_code=201, summary="Cria um novo usuario (somente admin)",
    dependencies=[Depends(require_admin)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return UserService(db).create_user(payload)


@router.patch(
    "/me/theme",
    response_model=UserOut,
    summary="Atualiza a preferencia de tema do usuario autenticado",
)
def update_my_theme(
    payload: ThemePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return UserService(db).update_theme_preference(current_user, payload)


@router.get(
    "/{user_id}", response_model=UserOut, summary="Detalha um usuario (admin e analistas)",
    dependencies=[Depends(require_analyst_or_admin)],
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return UserService(db).get_user(user_id)


@router.put(
    "/{user_id}", response_model=UserOut, summary="Atualiza um usuario (somente admin)",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    return UserService(db).update_user(user_id, payload, current_user)


@router.delete(
    "/{user_id}", response_model=MessageResponse, summary="Remove um usuario (somente admin)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MessageResponse:
    UserService(db).delete_user(user_id, current_user)
    return MessageResponse(message="Usuario removido com sucesso")


@router.post(
    "/{user_id}/reset-password", response_model=UserOut, summary="Redefine a senha de um usuario (somente admin)",
    dependencies=[Depends(require_admin)],
)
def reset_password(user_id: int, payload: UserPasswordReset, db: Session = Depends(get_db)) -> User:
    return UserService(db).reset_password(user_id, payload)


@router.post(
    "/{user_id}/activate", response_model=UserOut, summary="Ativa um usuario (somente admin)",
)
def activate_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
) -> User:
    return UserService(db).set_active(user_id, True, current_user)


@router.post(
    "/{user_id}/deactivate", response_model=UserOut, summary="Desativa um usuario (somente admin)",
)
def deactivate_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
) -> User:
    return UserService(db).set_active(user_id, False, current_user)
