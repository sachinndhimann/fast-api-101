# Workflow: Publish a domain event to Kafka for multiple consumers

## Problem
Something happening in your system (e.g. "OrderCreated") needs to be consumed by multiple, independent
downstream systems (analytics, notifications, a data warehouse), not just one worker doing one job.

## Investigation
Confirm this is genuinely a "many interested parties" situation, not a single discrete task — chapter
16's decision table: multiple independent consumers or replay needs point to Kafka, a single task points
to RabbitMQ or Celery instead.

## Implementation
Stand up Kafka (`docker compose up -d zookeeper kafka`). Publish events (chapter 15) keyed by the
relevant entity ID (e.g. `order_id`) so all events for one entity stay ordered relative to each other.
Each downstream system runs its own consumer, in its own consumer group, reading independently.

## Testing
Test the producer in isolation (confirm the correct topic, key, and payload shape). Test each consumer
in isolation by feeding it known messages and asserting on its processing result — you don't need a
running Kafka broker to unit-test a consumer's message-handling logic if it's factored out from the
polling loop.

## Validation
Run two consumers in the same group and confirm Kafka splits partitions between them; run two consumers
in *different* groups and confirm both receive every message independently.

## Production considerations
Plan topic retention and partition count deliberately up front (chapter 15) — partition count sets a
hard ceiling on in-group consumer parallelism, and increasing it later doesn't fix ordering guarantees
for data already written under the old partition count.
