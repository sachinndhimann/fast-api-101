# Workflow: Scale a FastAPI service horizontally

## Problem
A single instance of your API is at capacity, and you need to run multiple instances behind a load
balancer to handle more traffic.

## Investigation
**Before adding instances**: audit every piece of state in the app for chapter 20's statelessness
requirement — in-memory caches, in-memory rate limiters, in-memory session stores, any module-level
mutable state. Each must move to Redis/the database or be explicitly acceptable as per-instance-only.

## Implementation
Move any in-memory state found above to Redis (chapters 10, 12). Confirm connection pool sizing
(chapter 4) accounts for the new instance count: `N instances × pool_size < Postgres max_connections`.
Configure your load balancer/orchestrator to route based on readiness (chapter 22), not just "is the
process running."

## Testing
Simulate the scale-up locally: run 2 instances of the app pointed at the same Redis/Postgres, alternate
requests between them (chapter 20's test pattern), and confirm behavior (rate limits, cached data,
sessions) stays consistent regardless of which instance served a given request.

## Validation
Load test with concurrent requests distributed across instances and confirm latency/error rates don't
regress compared to the single-instance baseline.

## Production considerations
Roll out the scale-up gradually (2 instances, verify, then more) rather than jumping straight to peak
capacity — this surfaces state bugs (chapter 20) against real traffic at a survivable scale, not the worst
possible moment.
