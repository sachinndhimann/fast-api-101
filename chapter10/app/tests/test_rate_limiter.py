import asyncio
import pytest
import fakeredis.aioredis as fakeredis
from app.rate_limiter import TokenBucketRateLimiter


@pytest.mark.asyncio
async def test_burst_then_reject():
    r = fakeredis.FakeRedis()
    limiter = TokenBucketRateLimiter(r, capacity=3, refill_rate=1.0)
    results = [(await limiter.allow("ip-1"))[0] for _ in range(5)]
    assert results == [True, True, True, False, False]


@pytest.mark.asyncio
async def test_refill_over_time():
    r = fakeredis.FakeRedis()
    limiter = TokenBucketRateLimiter(r, capacity=2, refill_rate=10.0)
    assert (await limiter.allow("ip-2"))[0] is True
    assert (await limiter.allow("ip-2"))[0] is True
    assert (await limiter.allow("ip-2"))[0] is False
    await asyncio.sleep(0.15)
    assert (await limiter.allow("ip-2"))[0] is True


@pytest.mark.asyncio
async def test_keys_are_isolated_per_client():
    r = fakeredis.FakeRedis()
    limiter = TokenBucketRateLimiter(r, capacity=1, refill_rate=0.1)
    assert (await limiter.allow("ip-a"))[0] is True
    assert (await limiter.allow("ip-a"))[0] is False
    # a different key has its own independent bucket
    assert (await limiter.allow("ip-b"))[0] is True
