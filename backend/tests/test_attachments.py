"""Testes de anexos: upload valido, tipo invalido, tamanho invalido, download e exclusao."""
import io

from tests.conftest import auth_headers


def _create_request(client, headers):
    payload = {
        "title": "Solicitar revisao de contrato",
        "description": "Preciso que o juridico revise o contrato anexado.",
        "category": "ADMINISTRATIVO",
        "priority": "MEDIA",
    }
    return client.post("/api/v1/requests", json=payload, headers=headers).json()


def test_upload_anexo_valido(client, common_user):
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)

    files = {"file": ("contrato.pdf", io.BytesIO(b"%PDF-1.4 conteudo de teste"), "application/pdf")}
    response = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "contrato.pdf"
    assert body["size_bytes"] > 0


def test_upload_anexo_tipo_nao_permitido(client, common_user):
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)

    files = {"file": ("script.exe", io.BytesIO(b"MZ conteudo binario"), "application/octet-stream")}
    response = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers)
    assert response.status_code == 400


def test_upload_anexo_tamanho_excedido(client, common_user, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 10)  # 10 bytes, para forcar o limite
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)

    files = {"file": ("grande.txt", io.BytesIO(b"conteudo maior que dez bytes"), "text/plain")}
    response = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers)
    assert response.status_code == 400


def test_download_anexo_autorizado(client, common_user):
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)
    files = {"file": ("nota.txt", io.BytesIO(b"conteudo de nota"), "text/plain")}
    uploaded = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers).json()

    response = client.get(f"/api/v1/attachments/{uploaded['id']}/download", headers=headers)
    assert response.status_code == 200
    assert response.content == b"conteudo de nota"


def test_download_anexo_nao_autorizado_para_outro_usuario(client, common_user, db_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    outro = User(
        name="Outro Usuario Anexos", email="outro.anexos@example.com",
        hashed_password=hash_password("senha123"), role=UserRole.USER, is_active=True,
    )
    db_session.add(outro)
    db_session.commit()

    headers_owner = auth_headers(client, common_user.email)
    request = _create_request(client, headers_owner)
    files = {"file": ("privado.txt", io.BytesIO(b"conteudo privado"), "text/plain")}
    uploaded = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers_owner).json()

    headers_outro = auth_headers(client, outro.email)
    response = client.get(f"/api/v1/attachments/{uploaded['id']}/download", headers=headers_outro)
    assert response.status_code == 403


def test_download_anexo_inexistente(client, common_user):
    headers = auth_headers(client, common_user.email)
    response = client.get("/api/v1/attachments/999999/download", headers=headers)
    assert response.status_code == 404


def test_stored_filename_nao_e_previsivel_nem_usa_nome_original(client, common_user):
    """O nome interno do arquivo deve ser aleatorio (uuid), nunca o nome enviado pelo cliente,
    o que evita colisoes, sobrescrita e tentativas de path traversal via nome de arquivo."""
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)
    files = {"file": ("../../etc/passwd.txt", io.BytesIO(b"tentativa maliciosa"), "text/plain")}
    response = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers)
    assert response.status_code == 201
    body = response.json()
    # O nome original e preservado apenas como metadado de exibicao...
    assert body["original_filename"] == "../../etc/passwd.txt"
    # ...mas o arquivo fisico nunca deve ser gravado fora do diretorio de uploads.
    from pathlib import Path

    from app.core.config import settings

    upload_dir = Path(settings.UPLOAD_DIRECTORY).resolve()
    stored_files = list(upload_dir.glob("*.txt"))
    assert all(upload_dir in f.resolve().parents for f in stored_files)


def test_excluir_anexo_proprio(client, common_user):
    headers = auth_headers(client, common_user.email)
    request = _create_request(client, headers)
    files = {"file": ("removivel.txt", io.BytesIO(b"conteudo"), "text/plain")}
    uploaded = client.post(f"/api/v1/requests/{request['id']}/attachments", files=files, headers=headers).json()

    response = client.delete(f"/api/v1/attachments/{uploaded['id']}", headers=headers)
    assert response.status_code == 200

    download = client.get(f"/api/v1/attachments/{uploaded['id']}/download", headers=headers)
    assert download.status_code == 404
