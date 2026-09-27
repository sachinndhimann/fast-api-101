# Workflow: Move a slow synchronous operation to RabbitMQ

## Problem
An endpoint's response time is coupled to a slow, non-critical-path operation (e.g. sending an email)
that doesn't need to complete before responding to the caller (chapter 13).

## Investigation
Confirm the operation genuinely doesn't need to succeed before responding — if the caller needs to know
definitively "yes this happened" before your API call returns, this isn't a good candidate for
async/queue-based deferral.

## Implementation
Stand up RabbitMQ (`docker compose up -d rabbitmq`). Add a producer call (chapter 14) at the point in
your route where the slow operation currently happens, replacing the direct call. Build a separate
worker process that consumes the queue and performs the actual work, with manual acks and a bounded
retry-then-dead-letter policy.

## Testing
Test the API in isolation (it should now respond fast, without needing RabbitMQ running at all if you
mock the producer call) and the worker in isolation (feed it a message, confirm it processes correctly,
confirm it acks only on success).

## Validation
Confirm the message survives a worker crash: publish a message, kill the worker mid-processing, restart
it, and confirm the message is still processed (not lost) — this is exactly what manual acking protects.

## Production considerations
Deploy the worker as its own process/container, scaled independently of the API — that independent
scaling is a major part of the point of moving this work off the request path in the first place.
