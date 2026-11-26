from uuid import uuid4
from app.core.config import settings
from app.models.request import Request
from tests.conftest import auth_headers

def test_public_replies_scope_and_shadow_protection(client, db_session, admin_user, monkeypatch):
    monkeypatch.setattr(settings, "NEXOTIVA_INTEGRATION_TOKEN", "x"*40)
    base="/api/v1/integrations/nexotiva/tickets"
    headers={"Authorization":"Bearer "+"x"*40}
    scope={"company_id":str(uuid4()),"user_id":str(uuid4())}
    body={**scope,"company_name":"Alfa","user_name":"Cliente","user_email":"cliente@example.com",
          "module_slug":"demo","module_name":"Demo","client_request_id":str(uuid4()),
          "title":"Erro exemplo","description":"Detalhes exemplo","category":"TI","priority":"MEDIA"}
    r=client.post(base,json=body,headers=headers)
    assert r.status_code==201,r.text
    tid=r.json()["id"]
    assert client.post(base,json={**body,"title":"Outro"},headers=headers).status_code==409
    admin=auth_headers(client,admin_user.email)
    shadow=db_session.get(Request,tid).requester_id
    assert client.post(f"/api/v1/users/{shadow}/activate",headers=admin).status_code==403
    assert client.post(f"/api/v1/requests/{tid}/comments",json={"content":"Nota privada"},headers=admin).status_code==201
    assert client.post(f"/api/v1/requests/{tid}/comments",json={"content":"Resposta pública","public_reply":True},headers=admin).status_code==201
    url=f"{base}/{tid}/comments"
    assert [c["content"] for c in client.get(url,params=scope,headers=headers).json()]==["Resposta pública"]
    assert client.get(url,params={**scope,"user_id":str(uuid4())},headers=headers).status_code==404
    msg={"content":"Minha resposta","client_request_id":str(uuid4())}
    assert client.post(url,params=scope,json=msg,headers=headers).status_code==201
    assert client.post(url,params=scope,json=msg,headers=headers).status_code==201
    assert client.post(url,params=scope,json={**msg,"content":"Outro"},headers=headers).status_code==409
    assert len(client.get(url,params=scope,headers=headers).json())==2
