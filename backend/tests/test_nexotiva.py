from uuid import uuid4
from app.core.config import settings
from app.models.request import Request
from app.models.enums import RequestStatus
from tests.conftest import auth_headers

def test_nexotiva_integration_scope_and_idempotency(client, db_session, admin_user, common_user, monkeypatch):
    monkeypatch.setattr(settings, "NEXOTIVA_INTEGRATION_TOKEN", "test-only-" + "a"*40)
    base = "/api/v1/integrations/nexotiva/tickets"
    headers = {"Authorization": "Bearer " + settings.NEXOTIVA_INTEGRATION_TOKEN}
    body = dict(company_id=str(uuid4()), company_name="Empresa A", user_id=str(uuid4()), user_name="Cliente",
                user_email="cliente@example.com", module_slug="financeiro", module_name="Financeiro",
                client_request_id=str(uuid4()), title="Erro de teste", description="Detalhes do erro", category="TI", priority="MEDIA")
    assert client.post(base, json=body).status_code == 401
    assert client.post(base, json=body, headers={"Authorization":"Bearer wrong"}).status_code == 401
    res = client.post(base, json=body, headers=headers)
    assert res.status_code == 201, res.text
    tid = res.json()["id"]
    assert client.post(base, json=body, headers=headers).json()["id"] == tid
    scope = {k:body[k] for k in ("company_id","user_id")}
    assert client.get(base, params=scope, headers=headers).json()["total"] == 1
    assert client.get(base, params={**scope,"user_id":str(uuid4())}, headers=headers).json()["total"] == 0
    assert client.get(f"{base}/{tid}", params={**scope,"company_id":str(uuid4())}, headers=headers).status_code == 404
    assert client.get(f"{base}/{tid}", params={**scope,"user_id":str(uuid4())}, headers=headers).status_code == 404
    admin = auth_headers(client, admin_user.email)
    assert client.get(f"/api/v1/requests/{tid}", headers=admin).status_code == 200
    user = auth_headers(client, common_user.email)
    assert client.get(f"/api/v1/requests/{tid}/comments", headers=user).status_code == 403
    assert client.post(f"/api/v1/requests/{tid}/comments", json={"content":"teste"}, headers=user).status_code == 403
    row = db_session.get(Request, tid)
    row.status = RequestStatus.EM_ANDAMENTO
    db_session.commit()
    assert client.get(f"{base}/{tid}", params=scope, headers=headers).json()["status"] == "EM_ANDAMENTO"
