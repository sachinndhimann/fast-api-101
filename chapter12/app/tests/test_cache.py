import pytest
import fakeredis.aioredis as fakeredis
from httpx import ASGITransport, AsyncClient
import app.main as main_module


@pytest.fixture(autouse=True)
def patch_redis(monkeypatch):
    """Swap the real Redis client for fakeredis, and reset DB call counter, per test."""
    fake = fakeredis.FakeRedis()
    monkeypatch.setattr(main_module, "redis", fake)
    monkeypatch.setattr(main_module.cache, "redis", fake)
    main_module.DB_CALL_COUNT["count"] = 0
    main_module.FAKE_DB.clear()
    main_module.FAKE_DB[1] = {"id": 1, "name": "Widget", "price_cents": 999}


@pytest.mark.asyncio
async def test_second_read_hits_cache_not_db():
    transport = ASGITransport(app=main_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.get("/products/1")
        assert r1.json()["source"] == "database"
        r2 = await client.get("/products/1")
        assert r2.json()["source"] == "cache"

        debug = await client.get("/_debug/db-call-count")
        assert debug.json()["count"] == 1  # DB was hit exactly once across both reads


@pytest.mark.asyncio
async def test_write_invalidates_cache():
    transport = ASGITransport(app=main_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/products/1")  # populates cache
        await client.put("/products/1", params={"name": "Widget v2", "price_cents": 1499})
        r = await client.get("/products/1")
        assert r.json()["source"] == "database"  # cache was invalidated, so this is a fresh DB read
        assert r.json()["name"] == "Widget v2"
