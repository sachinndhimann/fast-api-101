# Workflow: Add resilience when a dependency your service calls goes down

## Problem
Your service calls another service or external API (chapter 18), and that dependency's occasional
outages are currently taking your service down with it.

## Investigation
Confirm you have a timeout configured on the call at all (chapter 18's `httpx` example) — an
unbounded-timeout call is often the actual root cause, more than a missing circuit breaker.

## Implementation
Add, in order of typical priority: (1) an explicit timeout, if missing, (2) retry with exponential
backoff for transient failures only (chapter 21's `tenacity` pattern, filtered by exception type), (3) a
circuit breaker if the dependency fails often enough that fast-failing is better than repeatedly timing
out (chapter 21).

## Testing
Chapter 21's test pattern: simulate the dependency failing N times in a row and assert the circuit opens;
simulate recovery after the cooldown and assert it closes again; simulate a permanent (non-retryable)
failure and confirm it's NOT retried needlessly.

## Validation
In a staging environment, actually kill/block the dependency and confirm your service degrades
gracefully (fast failures or a fallback response) instead of hanging or cascading.

## Production considerations
Alert specifically on circuit breakers opening (chapter 21) — this is a clean, high-signal indicator that
a real dependency outage is happening right now.
