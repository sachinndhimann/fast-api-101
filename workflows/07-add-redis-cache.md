# Workflow: Add caching to a read-heavy endpoint

## Problem
An endpoint is read far more often than the underlying data changes, and database load or latency has
become noticeable.

## Investigation
Confirm this endpoint is actually read-heavy relative to writes (check request logs/metrics if you have
them, chapter 22) — caching a rarely-read or frequently-changing resource adds complexity for little gain.

## Implementation
Follow chapter 12's cache-aside pattern: check cache, on miss read the DB and populate the cache with a
TTL, and explicitly invalidate (delete, don't overwrite) the cache key on every write path that touches
this data.

## Testing
Use `fakeredis` and an instrumented call counter (chapter 12's `DB_CALL_COUNT` pattern) to prove, not just
assert, that repeated reads hit the DB once and subsequent reads are served from cache, and that a write
correctly invalidates.

## Validation
Confirm every write path (not just the obvious `PUT`) that can change this data also invalidates the
cache — a common bug is remembering it on `PUT` but forgetting a bulk-update or admin endpoint.

## Production considerations
Watch your cache hit rate after deploying — if it's surprisingly low, either the TTL is too short for
your access pattern or the cache key design has an issue (e.g. accidentally including something that
varies per request that shouldn't).
