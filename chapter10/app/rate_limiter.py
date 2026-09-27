"""
Token bucket rate limiter backed by Redis. Distributed: every app instance
talks to the same Redis, so the limit is enforced across your whole fleet,
not per-process (a per-process in-memory limiter would let N instances each
independently allow the full limit -- N times the intended rate overall).
"""
import time
from redis.asyncio import Redis

# Lua script makes the read-check-write sequence ATOMIC on the Redis side --
# without this, two concurrent requests could both read "1 token left" and
# both be allowed through, a classic race condition (check-then-act across
# a network hop is never safe without a lock or an atomic script).
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])  -- tokens per second
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = math.max(0, now - last_refill)
tokens = math.min(capacity, tokens + elapsed * refill_rate)

local allowed = 0
if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
end

redis.call('HSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, 3600)

return {allowed, tokens}
"""


class TokenBucketRateLimiter:
    def __init__(self, redis: Redis, capacity: int = 5, refill_rate: float = 1.0):
        """
        capacity=5, refill_rate=1.0 means: burst up to 5 requests instantly,
        then sustain 1 request/second thereafter. Tune capacity for burst
        tolerance and refill_rate for sustained throughput -- they're
        independent knobs.
        """
        self.redis = redis
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._script = redis.register_script(TOKEN_BUCKET_LUA)

    async def allow(self, key: str, cost: int = 1) -> tuple[bool, float]:
        now = time.time()
        allowed, tokens_left = await self._script(
            keys=[f"ratelimit:{key}"],
            args=[self.capacity, self.refill_rate, now, cost],
        )
        return bool(allowed), float(tokens_left)
