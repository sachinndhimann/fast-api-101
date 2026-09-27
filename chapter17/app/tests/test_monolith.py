from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_order_creation_calls_payments_module_internally():
    r = client.post("/orders", params={"user_id": 1, "amount_cents": 5000})
    assert r.status_code == 201
    assert r.json()["status"] == "paid"

def test_order_for_unknown_user_fails_before_charging():
    r = client.post("/orders", params={"user_id": 999, "amount_cents": 5000})
    assert r.status_code == 404
