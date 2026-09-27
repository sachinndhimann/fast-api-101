# Background Job Options — Decision Table

| | FastAPI `BackgroundTasks` | Celery | RabbitMQ worker (ch. 14) | Kafka consumer (ch. 15) |
|---|---|---|---|---|
| Extra infrastructure | None | Broker (Redis/RabbitMQ) + workers | RabbitMQ | Kafka cluster |
| Survives API process restart | **No** | Yes (task sits in broker) | Yes | Yes |
| Automatic retries | No (write it yourself) | Yes, built in | Manual (you implement, ch. 14) | Manual (you implement) |
| Scales independently of API | No (same process) | Yes (separate workers) | Yes (separate workers) | Yes (separate consumers) |
| Good for | Cheap, best-effort, non-critical work | Scheduled/retryable discrete tasks | Discrete task distribution | High-throughput event streams, replay |
| Bad fit for | Anything that must survive a crash | Extremely high-throughput event streams | Event replay / multiple independent consumer types | Simple one-off fire-and-forget tasks |

## Choosing, in practice

- **Fire-and-forget, truly disposable** (a non-critical log line, a best-effort cache warm): `BackgroundTasks`.
- **Needs to survive a restart, wants retries, scheduling, or rate limiting per task type**: Celery.
- **A discrete task that must be reliably handed to exactly one worker, with retry/DLQ semantics you
  control precisely**: RabbitMQ (chapter 14).
- **An event that multiple independent consumers need to react to (or replay historically)**: Kafka
  (chapter 15).

A common trajectory: start with `BackgroundTasks` for genuinely disposable work, move to Celery once you
need reliability/retries without also needing multi-consumer event distribution, and reach for
RabbitMQ/Kafka directly once you're building genuine service-to-service event architecture rather than
"this one API needs to defer some of its own work."
