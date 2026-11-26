from tests.conftest import auth_headers
from app.models.request import Request

def test_revisions_are_scoped_and_rollback(db_session,client,admin_user,common_user,analyst_user):
    admin=auth_headers(client,admin_user.email)
    common=auth_headers(client,common_user.email)
    analyst=auth_headers(client,analyst_user.email)
    endpoint="/api/v1/sync/version"
    start=client.get(endpoint,headers=admin).json()["revision"]
    user_start=client.get(endpoint,headers=common).json()["revision"]
    body={"title":"Novo chamado","description":"Exemplo de chamado","category":"TI"}
    r=client.post("/api/v1/requests",headers=analyst,json=body)
    assert r.status_code==201,r.text
    assert client.get(endpoint,headers=admin).json()["revision"]!=start
    assert client.get(endpoint,headers=common).json()["revision"]==user_start
    current=client.get(endpoint,headers=admin).json()["revision"]
    row=db_session.get(Request,r.json()["id"])
    row.title="Mudança desfeita";db_session.flush();db_session.rollback()
    assert client.get(endpoint,headers=admin).json()["revision"]==current
