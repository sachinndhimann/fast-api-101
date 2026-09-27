import json
from redis.asyncio import Redis

PRODUCT_TTL_SECONDS = 300


class ProductCache:
    """
    Cache-aside pattern: the app code explicitly checks the cache, falls back
    to the DB on a miss, then populates the cache. Redis has no idea a
    "product" exists -- it's just a key/value store; the caching STRATEGY
    lives entirely here.
    """
    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, product_id: int) -> str:
        return f"product:{product_id}"

    async def get(self, product_id: int) -> dict | None:
        raw = await self.redis.get(self._key(product_id))
        return json.loads(raw) if raw else None

    async def set(self, product_id: int, data: dict):
        await self.redis.set(self._key(product_id), json.dumps(data), ex=PRODUCT_TTL_SECONDS)

    async def invalidate(self, product_id: int):
        """Called after POST/PUT/PATCH/DELETE -- see main.py. Never let a stale entry outlive a write."""
        await self.redis.delete(self._key(product_id))
