# Workflow: Debug a production incident on a live API

## Problem
Something is broken in production right now — elevated error rates, timeouts, or incorrect behavior
reported by users — and you need to find and fix it with minimum further disruption.

## Investigation
Start from metrics (chapter 22), not logs: which endpoint, what error rate, since when, correlated with
any recent deploy? Get a request ID (chapter 8/22) from an affected user's report if possible, and grep
logs for that exact ID across every service it touched (chapter 18).

## Implementation
Mitigate first, root-cause second, if the two are in tension: rollback a recent deploy, or flip a
feature flag, to stop user impact — then investigate the root cause without the pressure of an ongoing
incident.

## Testing
Once you've identified the bug, write a regression test that reproduces it before writing the fix — this
confirms your understanding of the bug is actually correct, not just plausible.

## Validation
Deploy the fix behind the same observability you used to detect the incident, and confirm the metric
that indicated the problem returns to baseline.

## Production considerations
Write an incident retrospective: what alerted you (or didn't — if you found out from a user, that's a
monitoring gap), how long detection took, how long mitigation took, and what would have caught this in
review or CI before it reached production.
