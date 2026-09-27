import os
from fastapi import FastAPI, HTTPException, status
from redis.asyncio import Redis
from app.cache import ProductCache

app = FastAPI(title="Chapter 12 - Caching")

redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
cache = ProductCache(redis)

# Stands in for a slow database (chapter 4 shows the real thing).
FAKE_DB = {1: {"id": 1, "name": "Widget", "price_cents": 999}}
DB_CALL_COUNT = {"count": 0}  # instrumented purely so tests/demo can prove caching works


async def fetch_from_db(product_id: int) -> dict | None:
    DB_CALL_COUNT["count"] += 1
    return FAKE_DB.get(product_id)


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Cache-aside read: check cache, on miss hit the DB and populate the cache."""
    cached = await cache.get(product_id)
    if cached is not None:
        return {**cached, "source": "cache"}

    product = await fetch_from_db(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await cache.set(product_id, product)
    return {**product, "source": "database"}


@app.put("/products/{product_id}")
async def update_product(product_id: int, name: str, price_cents: int):
    """
    Write-then-invalidate: update the source of truth, then DELETE the cache
    entry (don't just overwrite it -- deleting is simpler and avoids a race
    where a slow write "wins" over a fresher invalidate).
    """
    if product_id not in FAKE_DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    FAKE_DB[product_id] = {"id": product_id, "name": name, "price_cents": price_cents}
    await cache.invalidate(product_id)
    return FAKE_DB[product_id]


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    FAKE_DB.pop(product_id, None)
    await cache.invalidate(product_id)


@app.get("/_debug/db-call-count")
async def debug_db_call_count():
    """Not a real production endpoint -- exists purely to make caching's effect observable in the demo/tests."""
    return DB_CALL_COUNT
