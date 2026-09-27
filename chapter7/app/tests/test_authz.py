from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def h(email): return {"X-User-Email": email}

def test_user_can_read_own_profile():
    r = client.get("/profiles/carol@example.com", headers=h("carol@example.com"))
    assert r.status_code == 200

def test_user_cannot_read_others_profile():
    r = client.get("/profiles/dave@example.com", headers=h("carol@example.com"))
    assert r.status_code == 403

def test_manager_can_read_teammates_profile():
    r = client.get("/profiles/carol@example.com", headers=h("bob@example.com"))
    assert r.status_code == 200

def test_manager_can_read_team_data_user_cannot():
    r = client.get("/team-data", headers=h("bob@example.com"))
    assert r.status_code == 200
    r = client.get("/team-data", headers=h("carol@example.com"))
    assert r.status_code == 403

def test_only_admin_can_delete_user():
    r = client.delete("/users/carol@example.com", headers=h("bob@example.com"))
    assert r.status_code == 403
    r = client.delete("/users/carol@example.com", headers=h("alice@example.com"))
    assert r.status_code == 200
