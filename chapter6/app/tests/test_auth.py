from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_auth_flow():
    r = client.post("/auth/register", json={"email": "ada@example.com", "password": "hunter22"})
    assert r.status_code == 201

    r = client.post("/auth/login", data={"username": "ada@example.com", "password": "hunter22"})
    assert r.status_code == 200
    tokens = r.json()
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    r = client.get("/users/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["email"] == "ada@example.com"

    # wrong password
    r = client.post("/auth/login", data={"username": "ada@example.com", "password": "wrong"})
    assert r.status_code == 401

    # no token
    r = client.get("/users/me")
    assert r.status_code == 401

    # refresh rotates the token
    r = client.post("/auth/refresh", params={"refresh_token": refresh})
    assert r.status_code == 200
    new_refresh = r.json()["refresh_token"]
    assert new_refresh != refresh

    # old refresh token is now dead
    r = client.post("/auth/refresh", params={"refresh_token": refresh})
    assert r.status_code == 401
