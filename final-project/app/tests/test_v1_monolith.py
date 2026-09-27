import pytest
pytestmark = pytest.mark.asyncio

async def test_full_order_flow(client):
    r = await client.post("/products", params={"name": "Widget", "price_cents": 999})
    assert r.status_code == 201
    product_id = r.json()["id"]

    r = await client.post("/orders", params={"product_id": product_id, "quantity": 2})
    assert r.status_code == 201
    assert r.json()["status"] == "paid"

async def test_order_for_missing_product_fails(client):
    r = await client.post("/orders", params={"product_id": 9999, "quantity": 1})
    assert r.status_code == 404
