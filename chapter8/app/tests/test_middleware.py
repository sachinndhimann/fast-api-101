from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request_id_is_generated_and_echoed():
    r = client.get("/ping")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert r.json()["request_id"] == r.headers["X-Request-ID"]

def test_request_id_is_honored_if_provided():
    r = client.get("/ping", headers={"X-Request-ID": "fixed-id-123"})
    assert r.headers["X-Request-ID"] == "fixed-id-123"
