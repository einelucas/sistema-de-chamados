"""Testes do dashboard: totais globais para admin/analista, escopo pessoal para usuario comum."""
from tests.conftest import auth_headers


def _create_request(client, headers, title):
    payload = {
        "title": title,
        "description": "Descricao de teste para o dashboard.",
        "category": "TI",
        "priority": "ALTA",
    }
    return client.post("/api/v1/requests", json=payload, headers=headers).json()


def test_dashboard_admin_ve_totais_globais(client, admin_user, common_user, db_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    outro = User(
        name="Outro Solicitante", email="outro.dash@example.com",
        hashed_password=hash_password("senha123"), role=UserRole.USER, is_active=True,
    )
    db_session.add(outro)
    db_session.commit()

    _create_request(client, auth_headers(client, common_user.email), "Pedido do usuario comum")
    _create_request(client, auth_headers(client, outro.email), "Pedido de outro usuario")

    headers_admin = auth_headers(client, admin_user.email)
    response = client.get("/api/v1/dashboard/summary", headers=headers_admin)
    assert response.status_code == 200
    assert response.json()["total_requests"] == 2


def test_dashboard_usuario_comum_ve_apenas_o_proprio_escopo(client, common_user, db_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    outro = User(
        name="Outro Solicitante Dashboard", email="outro.dash2@example.com",
        hashed_password=hash_password("senha123"), role=UserRole.USER, is_active=True,
    )
    db_session.add(outro)
    db_session.commit()

    _create_request(client, auth_headers(client, common_user.email), "Pedido proprio")
    _create_request(client, auth_headers(client, outro.email), "Pedido de outra pessoa")

    headers_user = auth_headers(client, common_user.email)
    response = client.get("/api/v1/dashboard/summary", headers=headers_user)
    assert response.status_code == 200
    # o usuario comum deve ver apenas a propria solicitacao, nao o total global (2)
    assert response.json()["total_requests"] == 1
