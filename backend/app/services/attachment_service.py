"""Regras de negocio de anexos: validacao, armazenamento seguro e remocao."""
import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.attachment import Attachment
from app.models.enums import HistoryAction, UserRole
from app.models.user import User
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.request_repository import RequestRepository
from app.services.history_service import HistoryService


class AttachmentService:
    def __init__(self, db: Session) -> None:
        self.repo = AttachmentRepository(db)
        self.requests = RequestRepository(db)
        self.history = HistoryService(db)
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)


    def list_for_request(self, request_id: int) -> list[Attachment]:
        if not self.requests.get_by_id(request_id):
            raise NotFoundError("Solicitacao nao encontrada")
        return self.repo.list_by_request(request_id)

    def upload(self, request_id: int, file: UploadFile, user: User, shared_with_customer: bool=False) -> Attachment:
        if not self.requests.get_by_id(request_id):
            raise NotFoundError("Solicitacao nao encontrada")

        original_name = file.filename or "arquivo"
        extension = Path(original_name).suffix.lower()
        if extension not in settings.allowed_upload_extensions_list:
            raise AppError(f"Tipo de arquivo nao permitido: {extension}")

        limit=min(settings.MAX_UPLOAD_SIZE,3*1024*1024) if shared_with_customer or settings.is_production else settings.MAX_UPLOAD_SIZE
        contents = file.file.read(limit + 1)
        if len(contents) > limit:
            raise AppError("Arquivo excede o tamanho maximo permitido")

        # Gera um nome de arquivo seguro e unico para evitar sobrescrita ou path traversal
        safe_name = f"{uuid.uuid4().hex}{extension}"

        attachment = Attachment(
            request_id=request_id,
            uploaded_by_id=user.id,
            original_filename=original_name,
            stored_filename=safe_name,
            content_type=file.content_type or "application/octet-stream",
            size_bytes=len(contents),
            file_content=contents,
            shared_with_customer=shared_with_customer,
        )
        attachment = self.repo.create(attachment)
        self.history.log(request_id, user.id, HistoryAction.ANEXO_ADICIONADO, new_value=original_name)
        return attachment

    def get_file_path(self, attachment_id: int) -> tuple[Attachment, Path | None]:
        attachment = self.repo.get_by_id(attachment_id)
        if not attachment:
            raise NotFoundError("Anexo nao encontrado")
        if attachment.file_content is not None:
            return attachment, None
        # Garante que o arquivo resolvido permanece dentro do diretorio de uploads
        path = (self.upload_dir / attachment.stored_filename).resolve()
        if self.upload_dir.resolve() not in path.parents:
            raise AppError("Caminho de arquivo invalido")
        if not path.exists():
            raise NotFoundError("Arquivo nao encontrado no armazenamento")
        return attachment, path

    def delete(self, attachment_id: int, user: User) -> None:
        attachment = self.repo.get_by_id(attachment_id)
        if not attachment:
            raise NotFoundError("Anexo nao encontrado")
        request = self.requests.get_by_id(attachment.request_id)
        if not request or (user.role == UserRole.USER and user.id not in (request.requester_id, request.assignee_id)):
            raise ForbiddenError('Sem acesso ao chamado')
        if user.role != UserRole.ADMIN and attachment.uploaded_by_id != user.id:
            raise ForbiddenError("Voce nao tem permissao para remover este anexo")
        path = self.upload_dir / attachment.stored_filename
        self.repo.delete(attachment)
        if path.resolve().is_relative_to(self.upload_dir.resolve()) and path.exists():
            os.remove(path)
