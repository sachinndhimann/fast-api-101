# Workflow: Deploy a new version of the API to production

## Problem
You have a tested, merged change and need to get it into production safely, without dropping requests
or requiring manual intervention.

## Investigation
Confirm: does this change include a database migration? If so, is it backward-compatible with the
currently-running old code (needed during a rolling deploy, where old and new code run simultaneously
for a period)?

## Implementation
Follow chapter 25's pipeline: CI runs tests → builds a Docker image → pushes to a registry → triggers a
rolling deploy. Run database migrations as their own step, before the new application version starts
receiving traffic.

## Testing
CI's test suite is the gate — no image should be built, let alone deployed, from code that fails tests
(chapter 25's `needs: test` dependency in the example pipeline).

## Validation
Watch error rates and latency (chapter 22) during and immediately after the rollout; confirm readiness
probes are correctly gating traffic to new pods (chapter 22) and graceful shutdown (chapter 25) is letting
old pods finish in-flight work.

## Production considerations
Have a rollback plan ready before you deploy, not improvised during an incident — for most setups this
is "redeploy the previous image tag," which should be a one-command operation.
