"""Rotas de anexos: upload, listagem, download protegido e remocao."""
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.attachment import AttachmentOut
from app.schemas.common import MessageResponse
from app.services.attachment_service import AttachmentService
from app.services.request_service import RequestService

router = APIRouter(tags=["Anexos"])


@router.get(
    "/requests/{request_id}/attachments", response_model=list[AttachmentOut], summary="Lista anexos da solicitacao"
)
def list_attachments(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RequestService(db).get_request(request_id, current_user)
    return AttachmentService(db).list_for_request(request_id)


@router.post(
    "/requests/{request_id}/attachments",
    response_model=AttachmentOut,
    status_code=201,
    summary="Anexa um arquivo a solicitacao",
)
def upload_attachment(
    request_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    RequestService(db).get_request(request_id, current_user)
    return AttachmentService(db).upload(request_id, file, current_user)


@router.get("/attachments/{attachment_id}/download", summary="Baixa um anexo (rota protegida)")
def download_attachment(attachment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AttachmentService(db)
    attachment, path = service.get_file_path(attachment_id)
    # Garante que o usuario tem permissao de visualizar a solicitacao dona do anexo
    RequestService(db).get_request(attachment.request_id, current_user)
    return FileResponse(path=path, filename=attachment.original_filename, media_type=attachment.content_type)


@router.delete("/attachments/{attachment_id}", response_model=MessageResponse, summary="Remove um anexo")
def delete_attachment(attachment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AttachmentService(db).delete(attachment_id, current_user)
    return MessageResponse(message="Anexo removido com sucesso")
