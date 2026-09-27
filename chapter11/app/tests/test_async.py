"""
Proves the concurrency claim, not just the endpoint's correctness: hitting
/blocking-in-async twice concurrently takes ~2x as long as hitting
/actually-async twice concurrently, because the blocking version stalls the
whole event loop.
"""
import asyncio
import time
import pytest
import httpx
from httpx import ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_blocking_endpoint_serializes_concurrent_requests():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        await asyncio.gather(
            client.get("/blocking-in-async"),
            client.get("/blocking-in-async"),
        )
        elapsed = time.perf_counter() - start
    # two 1-second blocking calls concurrently should take close to 2s, not 1s,
    # because time.sleep() blocks the single-threaded event loop
    assert elapsed > 1.8, f"expected serialization (~2s), got {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_async_sleep_endpoint_runs_concurrently():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        await asyncio.gather(
            client.get("/actually-async"),
            client.get("/actually-async"),
        )
        elapsed = time.perf_counter() - start
    # two 1-second async sleeps concurrently should take close to 1s, not 2s
    assert elapsed < 1.5, f"expected concurrency (~1s), got {elapsed:.2f}s"
