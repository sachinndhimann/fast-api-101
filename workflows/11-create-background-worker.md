# Workflow: Create a new background worker process

## Problem
You need a long-running process, separate from your API, that consumes work from a queue (RabbitMQ,
Kafka) or runs scheduled jobs (Celery beat, a cron-triggered script).

## Investigation
Decide the shape: a queue consumer (event-driven, chapters 14-15), a Celery worker (task-based, chapter
16), or a scheduled job (runs on a timer, not triggered by an event).

## Implementation
Keep the worker's business logic in the SAME service-layer code your API uses where possible (chapter 3's
layering) — a worker calling `OrderService.mark_shipped()` should reuse the exact same service method an
API route would call, not duplicate the logic.
```python
# worker.py
def main():
    connection = connect_to_broker()
    while True:
        message = get_next_message(connection)
        process(message)  # calls into the SAME service layer as the API
```

## Testing
Unit test the message-processing function directly (feed it a fake message, assert on the resulting
service calls/state), separately from testing the actual broker connection/polling loop.

## Validation
Confirm the worker handles a malformed/unexpected message gracefully (logs and dead-letters or skips,
per chapter 14) rather than crashing the whole worker process on one bad message.

## Production considerations
Run multiple worker instances behind the same queue/consumer group for both throughput and fault
tolerance — a single-instance worker is a single point of failure for all queued work.
