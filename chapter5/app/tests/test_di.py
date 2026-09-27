from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user

client = TestClient(app)


def test_me_requires_token():
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_with_valid_token():
    resp = client.get("/me", headers={"Authorization": "Bearer token-alice"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


def test_dependency_override_for_testing():
    """This is THE reason DI exists for testability: swap real auth for a fake user, no token needed."""
    app.dependency_overrides[get_current_user] = lambda: {"id": 99, "name": "Test", "role": "admin"}
    try:
        resp = client.get("/me")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"
    finally:
        app.dependency_overrides.clear()
