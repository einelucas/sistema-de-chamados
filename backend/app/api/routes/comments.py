"""Rotas de comentarios de uma solicitacao."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut, CommentUpdate
from app.schemas.common import MessageResponse
from app.services.comment_service import CommentService
from app.services.request_service import RequestService

router = APIRouter(tags=["Comentarios"])


@router.get("/requests/{request_id}/comments", response_model=list[CommentOut], summary="Lista comentarios")
def list_comments(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RequestService(db).get_request(request_id, current_user)
    return CommentService(db).list_comments(request_id)


@router.post(
    "/requests/{request_id}/comments", response_model=CommentOut, status_code=201, summary="Adiciona um comentario"
)
def create_comment(
    request_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    RequestService(db).get_request(request_id, current_user)
    return CommentService(db).create_comment(request_id, payload, current_user)


@router.put("/comments/{comment_id}", response_model=CommentOut, summary="Edita um comentario proprio")
def update_comment(
    comment_id: int, payload: CommentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return CommentService(db).update_comment(comment_id, payload, current_user)


@router.delete("/comments/{comment_id}", response_model=MessageResponse, summary="Exclui um comentario proprio")
def delete_comment(comment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommentService(db).delete_comment(comment_id, current_user)
    return MessageResponse(message="Comentario removido com sucesso")
