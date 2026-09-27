# Workflow: Add rate limiting to an endpoint or the whole API

## Problem
An endpoint (often auth-related) is vulnerable to abuse — brute force, scraping, or accidental traffic
storms from a buggy client.

## Investigation
Decide the granularity: per-IP (simplest, chapter 10's default), per-user/API-key (better for
authenticated APIs), or per-endpoint-specific-key (e.g. per-username on login, to prevent IP-rotation
bypass — chapter 10's exercise).

## Implementation
Stand up Redis (`docker compose up -d redis`), add chapter 10's `TokenBucketRateLimiter`, and either
apply it globally as middleware or selectively per-route as a dependency.

## Testing
Use `fakeredis` (chapter 10's test pattern) to test burst behavior and refill timing without needing a
real Redis process in your test suite.

## Validation
Manually burst the real endpoint past its limit and confirm a 429 with a `Retry-After` header, then wait
and confirm it recovers.

## Production considerations
Monitor 429 rates by endpoint and by key — a sudden spike is either an attack or a misconfigured limit;
both are worth knowing about quickly.
