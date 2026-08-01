"""Testes de administracao de usuarios e controle de acesso por papel."""
from tests.conftest import auth_headers


def test_usuario_comum_nao_acessa_administracao(client, common_user):
    headers = auth_headers(client, common_user.email)
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403


def test_analista_pode_listar_usuarios_para_atribuicao(client, analyst_user):
    headers = auth_headers(client, analyst_user.email)
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200


def test_analista_nao_pode_criar_usuario(client, analyst_user):
    headers = auth_headers(client, analyst_user.email)
    payload = {"name": "Tentativa", "email": "tentativa@teste.com", "password": "senha123"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 403


def test_admin_lista_usuarios(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_admin_cria_usuario(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    payload = {"name": "Novo Analista", "email": "novo.analista@teste.com", "password": "senha123", "role": "ANALYST"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["role"] == "ANALYST"


def test_admin_nao_pode_duplicar_email(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    payload = {"name": "Duplicado", "email": admin_user.email, "password": "senha123"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 409


def test_admin_nao_pode_excluir_a_propria_conta(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.delete(f"/api/v1/users/{admin_user.id}", headers=headers)
    assert response.status_code == 403


def test_admin_nao_pode_desativar_a_propria_conta(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.post(f"/api/v1/users/{admin_user.id}/deactivate", headers=headers)
    assert response.status_code == 403


def test_nao_pode_excluir_o_ultimo_administrador_ativo(client, db_session, admin_user):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    admin_b = User(
        name="Admin B", email="admin.b@example.com",
        hashed_password=hash_password("senha123"), role=UserRole.ADMIN, is_active=True,
    )
    db_session.add(admin_b)
    db_session.commit()
    db_session.refresh(admin_b)

    headers_b = auth_headers(client, admin_b.email)

    # admin_b exclui o admin original -> ok, pois admin_b continua sendo um admin ativo
    response = client.delete(f"/api/v1/users/{admin_user.id}", headers=headers_b)
    assert response.status_code == 200

    # agora admin_b e o unico admin ativo; sua autoexclusao ja e bloqueada pela regra de
    # autoexclusao, o que por consequencia impede o sistema de ficar sem nenhum admin.
    response = client.delete(f"/api/v1/users/{admin_b.id}", headers=headers_b)
    assert response.status_code == 403


def test_nao_pode_desativar_o_ultimo_administrador_ativo(client, db_session, admin_user):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    admin_b = User(
        name="Admin B Desativacao", email="admin.b.deact@example.com",
        hashed_password=hash_password("senha123"), role=UserRole.ADMIN, is_active=True,
    )
    db_session.add(admin_b)
    db_session.commit()
    db_session.refresh(admin_b)

    headers_b = auth_headers(client, admin_b.email)

    response = client.post(f"/api/v1/users/{admin_user.id}/deactivate", headers=headers_b)
    assert response.status_code == 200

    response = client.post(f"/api/v1/users/{admin_b.id}/deactivate", headers=headers_b)
    assert response.status_code == 403


def test_deletar_usuario_com_solicitacoes_vinculadas_retorna_conflito(client, admin_user, common_user):
    headers_admin = auth_headers(client, admin_user.email)
    headers_user = auth_headers(client, common_user.email)

    payload = {
        "title": "Solicitacao vinculada ao usuario",
        "description": "Usada para testar exclusao de usuario com dependencias.",
        "category": "TI",
    }
    client.post("/api/v1/requests", json=payload, headers=headers_user)

    response = client.delete(f"/api/v1/users/{common_user.id}", headers=headers_admin)
    assert response.status_code == 409



def test_usuario_atualiza_a_propria_preferencia_de_tema(client, common_user):
    headers = auth_headers(client, common_user.email)

    response = client.patch(
        "/api/v1/users/me/theme",
        json={"theme_preference": "dark"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["theme_preference"] == "dark"

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["theme_preference"] == "dark"


def test_preferencia_de_tema_invalida_e_rejeitada(client, common_user):
    headers = auth_headers(client, common_user.email)

    response = client.patch(
        "/api/v1/users/me/theme",
        json={"theme_preference": "sepia"},
        headers=headers,
    )

    assert response.status_code == 422
