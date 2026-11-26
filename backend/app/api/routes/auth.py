"""Rotas de autenticacao: login e usuario autenticado."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_session_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, ChangePassword
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login", response_model=TokenResponse, summary="Autentica um usuario e retorna um token")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService(db).login(payload)


@router.get("/me", response_model=UserOut, summary="Retorna os dados do usuario autenticado")
def read_me(current_user: User = Depends(get_session_user)) -> User:
    return current_user

@router.post("/change-password",response_model=TokenResponse)
def change_password(payload:ChangePassword,current_user:User=Depends(get_session_user),db:Session=Depends(get_db)):
    return AuthService(db).change_password(current_user,payload)
