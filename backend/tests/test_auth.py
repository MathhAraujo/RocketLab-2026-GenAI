def test_login_aceita_qualquer_credencial(client):
    r = client.post("/api/auth/login", json={"username": "qualquer", "password": "qualquer"})
    assert r.status_code == 200


def test_login_retorna_token_bearer(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_me_retorna_usuario(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert "username" in r.json()
