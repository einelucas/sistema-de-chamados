"""Testes de solicitacoes: criacao, listagem, atualizacao de status e regras de acesso."""
from tests.conftest import auth_headers


def _create_request(client, headers, title="Solicitar novo monitor"):
    payload = {
        "title": title,
        "description": "Preciso de um monitor adicional para o meu posto de trabalho.",
        "category": "TI",
        "priority": "MEDIA",
    }
    return client.post("/api/v1/requests", json=payload, headers=headers)


def test_criar_solicitacao(client, common_user):
    headers = auth_headers(client, common_user.email)
    response = _create_request(client, headers)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Solicitar novo monitor"
    assert body["status"] == "ABERTA"
    assert body["requester"]["email"] == common_user.email


def test_listar_solicitacoes(client, common_user):
    headers = auth_headers(client, common_user.email)
    _create_request(client, headers)
    response = client.get("/api/v1/requests", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1


def test_atualizar_status_como_analista(client, common_user, analyst_user):
    user_headers = auth_headers(client, common_user.email)
    created = _create_request(client, user_headers).json()

    analyst_headers = auth_headers(client, analyst_user.email)
    response = client.patch(
        f"/api/v1/requests/{created['id']}/status", json={"status": "EM_ANDAMENTO"}, headers=analyst_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "EM_ANDAMENTO"


def test_usuario_comum_nao_pode_alterar_status(client, common_user):
    headers = auth_headers(client, common_user.email)
    created = _create_request(client, headers).json()
    response = client.patch(
        f"/api/v1/requests/{created['id']}/status", json={"status": "EM_ANDAMENTO"}, headers=headers
    )
    assert response.status_code == 403


def test_usuario_nao_ve_solicitacao_de_outro(client, common_user, db_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    outro = User(
        name="Outro Usuario",
        email="outro@teste.com",
        hashed_password=hash_password("senha123"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(outro)
    db_session.commit()

    headers_outro = auth_headers(client, outro.email)
    created = _create_request(client, headers_outro).json()

    headers_common = auth_headers(client, common_user.email)
    response = client.get(f"/api/v1/requests/{created['id']}", headers=headers_common)
    assert response.status_code == 403


def test_filtro_por_status(client, common_user):
    headers = auth_headers(client, common_user.email)
    _create_request(client, headers)
    response = client.get("/api/v1/requests?status=ABERTA", headers=headers)
    assert response.status_code == 200
    assert all(item["status"] == "ABERTA" for item in response.json()["items"])


def test_validacao_campos_obrigatorios(client, common_user):
    headers = auth_headers(client, common_user.email)
    response = client.post("/api/v1/requests", json={"title": "ab"}, headers=headers)
    assert response.status_code == 422


def test_transicao_de_status_invalida_e_rejeitada(client, common_user, analyst_user):
    user_headers = auth_headers(client, common_user.email)
    created = _create_request(client, user_headers).json()

    analyst_headers = auth_headers(client, analyst_user.email)
    # nao e permitido pular de ABERTA diretamente para CONCLUIDA sem passar por EM_ANDAMENTO
    response = client.patch(
        f"/api/v1/requests/{created['id']}/status", json={"status": "CONCLUIDA"}, headers=analyst_headers
    )
    assert response.status_code == 400


def test_transicao_de_status_valida_para_conclusao(client, common_user, analyst_user):
    user_headers = auth_headers(client, common_user.email)
    created = _create_request(client, user_headers).json()
    analyst_headers = auth_headers(client, analyst_user.email)

    client.patch(f"/api/v1/requests/{created['id']}/status", json={"status": "EM_ANDAMENTO"}, headers=analyst_headers)
    response = client.patch(
        f"/api/v1/requests/{created['id']}/status", json={"status": "CONCLUIDA"}, headers=analyst_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CONCLUIDA"
    assert response.json()["completed_at"] is not None


def test_nao_pode_alterar_status_apos_concluida_exceto_reabrir(client, common_user, analyst_user):
    user_headers = auth_headers(client, common_user.email)
    created = _create_request(client, user_headers).json()
    analyst_headers = auth_headers(client, analyst_user.email)

    client.patch(f"/api/v1/requests/{created['id']}/status", json={"status": "EM_ANDAMENTO"}, headers=analyst_headers)
    client.patch(f"/api/v1/requests/{created['id']}/status", json={"status": "CONCLUIDA"}, headers=analyst_headers)

    response = client.patch(
        f"/api/v1/requests/{created['id']}/status", json={"status": "AGUARDANDO"}, headers=analyst_headers
    )
    assert response.status_code == 400


def test_exclusao_de_solicitacao_e_logica_e_registra_historico(client, common_user, admin_user, db_session):
    from app.models.enums import HistoryAction
    from app.models.history import RequestHistory
    from app.models.request import Request

    user_headers = auth_headers(client, common_user.email)
    created = _create_request(client, user_headers).json()

    admin_headers = auth_headers(client, admin_user.email)
    response = client.delete(f"/api/v1/requests/{created['id']}", headers=admin_headers)
    assert response.status_code == 200

    # a solicitacao foi excluida logicamente (nao aparece mais para o solicitante)...
    detail = client.get(f"/api/v1/requests/{created['id']}", headers=user_headers)
    assert detail.status_code == 404

    # ...mas o registro permanece no banco (exclusao logica, nao fisica)...
    db_request = db_session.get(Request, created["id"])
    assert db_request is not None
    assert db_request.is_deleted is True

    # ...e a acao de exclusao foi registrada no historico de auditoria.
    history_entries = (
        db_session.query(RequestHistory)
        .filter(RequestHistory.request_id == created["id"], RequestHistory.action == HistoryAction.EXCLUSAO)
        .all()
    )
    assert len(history_entries) == 1
