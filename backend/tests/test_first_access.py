from tests.conftest import auth_headers
from app.core.security import verify_password
def test_forced_change_and_old_token_revocation(client,db_session,admin_user):
    admin_user.must_change_password=True
    db_session.commit()
    old=auth_headers(client,admin_user.email)
    assert client.get("/api/v1/auth/me",headers=old).json()["must_change_password"]
    assert client.get("/api/v1/requests",headers=old).status_code==403
    url="/api/v1/auth/change-password"
    assert client.post(url,headers=old,json={"current_password":"wrong","new_password":"New-example-123456"}).status_code==401
    result=client.post(url,headers=old,json={"current_password":"senha123","new_password":"New-example-123456"})
    assert result.status_code==200,result.text
    assert not result.json()["user"]["must_change_password"]
    assert client.get("/api/v1/requests",headers=old).status_code==401
    headers={"Authorization":"Bearer "+result.json()["access_token"]}
    assert client.get("/api/v1/requests",headers=headers).status_code==200
    assert client.post("/api/v1/auth/login",json={"email":admin_user.email,"password":"senha123"}).status_code==401
