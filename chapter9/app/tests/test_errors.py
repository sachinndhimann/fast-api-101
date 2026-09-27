from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_not_found_uses_envelope():
    r = client.get("/products/999")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "request_id" in body["error"]

def test_out_of_stock():
    r = client.post("/orders", params={"product_id": 1, "quantity": 1})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "OUT_OF_STOCK"

def test_validation_error_uses_same_envelope_shape():
    r = client.post("/orders", params={"product_id": "not-a-number", "quantity": 1})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"

def test_unhandled_exception_does_not_leak_traceback():
    # TestClient re-raises server exceptions by default so tests fail loudly;
    # disable that here since we're deliberately testing the 500 handler itself.
    local_client = TestClient(app, raise_server_exceptions=False)
    r = local_client.get("/boom")
    assert r.status_code == 500
    body = r.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "ZeroDivisionError" not in r.text
