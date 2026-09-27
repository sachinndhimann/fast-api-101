# Workflow: Debug a slow API endpoint

## Problem
An endpoint (or the whole API) has become noticeably slower, and you need to find out why before
guessing at a fix.

## Investigation
Check, in this order: (1) is it slow for all requests or specific ones? (2) has data volume grown
recently (chapter 4's N+1 problem gets worse as tables grow)? (3) is it CPU-bound or I/O-bound (chapter
11)? (4) any recent deploys or dependency version changes around when it got slow?

## Implementation
Enable SQL query logging (`echo=True` on the engine, chapter 4) and count queries per request, not just
timing — a slow endpoint issuing 200 queries per request is a different bug than one issuing 2 slow
queries. Check for blocking calls inside `async def` routes (chapter 11) using a simple concurrent-request
timing test.

## Testing
Write a regression test that asserts an upper bound on query count for the specific endpoint (many ORMs
support a query-counting test helper) — this catches a future re-introduction of the same N+1 bug before
it reaches production again.

## Validation
Confirm the fix under realistic concurrency, not just a single sequential request — chapter 11's blocking
bug is specifically invisible under low concurrency.

## Production considerations
Add this endpoint's latency and query-count to your metrics dashboard (chapter 22) so a future
regression is caught by an alert, not a support ticket.
