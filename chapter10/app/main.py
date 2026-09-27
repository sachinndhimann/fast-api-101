import os
from fastapi import FastAPI, Request, HTTPException, status
from redis.asyncio import Redis
from app.rate_limiter import TokenBucketRateLimiter

app = FastAPI(title="Chapter 10 - Rate Limiting")

redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
limiter = TokenBucketRateLimiter(redis, capacity=5, refill_rate=1.0)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    IP-based limiting here for simplicity; swap the key for an API key or
    user id for per-user/per-tenant limiting -- the limiter itself doesn't
    care what the key represents.
    """
    client_ip = request.client.host if request.client else "unknown"
    allowed, tokens_left = await limiter.allow(key=client_ip)
    if not allowed:
        return _too_many_requests(tokens_left)
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(int(tokens_left))
    return response


def _too_many_requests(tokens_left: float):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": {"code": "RATE_LIMITED", "message": "Too many requests, slow down"}},
        headers={"Retry-After": "1"},
    )


@app.get("/ping")
async def ping():
    return {"message": "pong"}
