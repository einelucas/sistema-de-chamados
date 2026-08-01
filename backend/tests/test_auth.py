"""Testes de autenticacao: login valido, invalido e rota protegida."""
from tests.conftest import auth_headers


def test_login_valido(client, admin_user):
    response = client.post(
        "/api/v1/auth/login", json={"email": admin_user.email, "password": "senha123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user"]["email"] == admin_user.email
    assert body["user"]["theme_preference"] == "light"


def test_login_invalido(client, admin_user):
    response = client.post(
        "/api/v1/auth/login", json={"email": admin_user.email, "password": "senha-errada"}
    )
    assert response.status_code == 401


def test_rota_protegida_sem_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_rota_protegida_com_token(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == admin_user.email


def test_token_invalido_e_rejeitado(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401


def test_token_expirado_e_rejeitado(client, admin_user):
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    from app.core.config import settings

    expired_payload = {
        "sub": str(admin_user.id),
        "role": admin_user.role.value,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_login_usuario_inativo_e_rejeitado(client, db_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    inactive_user = User(
        name="Usuario Inativo",
        email="inativo@example.com",
        hashed_password=hash_password("senha123"),
        role=UserRole.USER,
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()

    response = client.post("/api/v1/auth/login", json={"email": "inativo@example.com", "password": "senha123"})
    assert response.status_code == 401


def test_usuario_desativado_apos_login_perde_acesso(client, db_session, common_user):
    headers = auth_headers(client, common_user.email)
    # confirma que o token funciona antes da desativacao
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    common_user.is_active = False
    db_session.commit()

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
