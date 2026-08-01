"""Testes de comentarios em solicitacoes."""
from tests.conftest import auth_headers


def test_adicionar_e_listar_comentarios(client, common_user):
    headers = auth_headers(client, common_user.email)
    request_payload = {
        "title": "Solicitar cadeira ergonomica",
        "description": "A cadeira atual esta com problemas.",
        "category": "ADMINISTRATIVO",
        "priority": "BAIXA",
    }
    created = client.post("/api/v1/requests", json=request_payload, headers=headers).json()

    comment_response = client.post(
        f"/api/v1/requests/{created['id']}/comments", json={"content": "Acompanhando esta solicitacao."}, headers=headers
    )
    assert comment_response.status_code == 201

    list_response = client.get(f"/api/v1/requests/{created['id']}/comments", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_editar_comentario_de_outro_usuario_falha(client, common_user, analyst_user):
    headers_user = auth_headers(client, common_user.email)
    request_payload = {
        "title": "Solicitar acesso ao sistema",
        "description": "Preciso de acesso ao sistema financeiro.",
        "category": "TI",
        "priority": "ALTA",
    }
    created = client.post("/api/v1/requests", json=request_payload, headers=headers_user).json()
    comment = client.post(
        f"/api/v1/requests/{created['id']}/comments", json={"content": "Comentario original"}, headers=headers_user
    ).json()

    headers_analyst = auth_headers(client, analyst_user.email)
    response = client.put(
        f"/api/v1/comments/{comment['id']}", json={"content": "Tentativa de edicao"}, headers=headers_analyst
    )
    assert response.status_code == 403
