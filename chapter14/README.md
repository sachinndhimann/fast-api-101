# Chapter 14 — RabbitMQ

## Concept

RabbitMQ is a message broker implementing AMQP: producers publish messages to **exchanges**, exchanges
route them to **queues** based on **bindings** and a **routing key**, and **consumers** pull messages
off queues.

## Why it exists

RabbitMQ is built for **task distribution and reliable delivery** between services — "make sure this
work item gets done, exactly-once-ish, even if a consumer briefly dies." It's the right tool when you
have discrete units of work to hand off (send this email, process this order), as opposed to Kafka's
strength in high-throughput event streams that multiple independent consumers replay (chapter 15).

## Mental model

```
Producer -> Exchange (routes by binding rules) -> Queue -> Consumer -> ack
```

The exchange is the router; the queue is the buffer; the binding + routing key decide which messages
land in which queue. This indirection is what lets you add a new consumer for the same event later
(bind a new queue to the same exchange) without touching the producer at all.

## Diagram

```mermaid
flowchart LR
    API[FastAPI: POST /orders] -->|publish routing_key=order.created| Ex[Exchange: orders, topic]
    Ex -->|binding: order.created| Q[Queue: order_created_q]
    Q --> W[Worker: worker.py]
    W -->|processing fails 3x| DLQ[Dead-letter queue]
```

## Setup

```bash
docker compose up -d rabbitmq
# Management UI: http://localhost:15672 (guest/guest)
```

## Realistic example

- `app/producer.py` — declares a durable `orders` topic exchange and a durable `order_created_q` queue,
  bound with routing key `order.created`, then publishes a persistent message.
- `app/worker.py` — consumes from that queue with **manual acknowledgement** (`auto_ack=False`):
  the message is only removed from the queue after `basic_ack`, so a worker crash mid-processing leaves
  the message for redelivery instead of silently losing it.
- `app/api.py` — the FastAPI app that publishes instead of doing the slow work inline (see chapter 13).

```bash
cd chapter14
PYTHONPATH=. python app/worker.py &     # start the worker
PYTHONPATH=. uvicorn app.api:app --reload --port 8000
curl -X POST "localhost:8000/orders?user_email=ada@example.com"
# watch the worker's terminal print "Processing OrderCreated..."
```

## Acknowledgement, retry, dead-letter

`worker.py`'s `handle_order_created` demonstrates the full lifecycle:
1. **Try to process.** On success: `basic_ack` — message is gone for good.
2. **On failure**, under the retry limit: republish with an incremented `x-retry-count` header, then ack
   the original (so it's not stuck in the queue while also being retried — this avoids duplicate
   in-flight copies).
3. **On failure**, at the retry limit: `basic_nack(requeue=False)` — with dead-lettering configured,
   this routes the message to `order_created_dlq` for manual inspection instead of losing it silently.

`basic_qos(prefetch_count=1)` ensures a worker isn't handed a new message until it acks the last one —
without this, a slow worker can be flooded with messages it hasn't gotten to yet, defeating fair
distribution across multiple worker processes.

## Common mistakes

- `auto_ack=True` for anything you actually care about losing — a worker crash between receiving and
  finishing a message means it's just gone, no redelivery.
- Non-durable queues/exchanges in production — a broker restart (deploy, crash, maintenance) wipes them
  and any messages that were in them.
- Using `requeue=True` for a message that will fail identically forever (a malformed payload) — this
  creates an infinite redelivery loop that pins CPU and floods logs, instead of dead-lettering after a
  bounded number of attempts.

## Production considerations

- Monitor queue depth — a steadily growing queue means consumers can't keep up; that's your signal to
  scale consumers horizontally (RabbitMQ hands out messages round-robin across consumers on the same
  queue automatically).
- Alert on dead-letter queue depth — every message there represents work that silently didn't happen;
  in most systems that's not something you want to only notice weeks later.
- Consider the RabbitMQ delayed-message-exchange plugin (or a separate TTL-queue trick) for real
  backoff between retries — a raw immediate requeue retries instantly, which is rarely what you want for
  a downstream dependency that's temporarily overloaded.

## Exercise

Add a second consumer, bound to the same `orders` exchange with routing key `order.#` (wildcard), that
logs every order-related event to a separate `audit_log_q` — without changing `producer.py` at all. This
is the payoff of exchange/binding indirection: new consumers, zero producer changes.

## Interview-style scenario

> "Two instances of `worker.py` are running, consuming from the same queue. A burst of 100 orders comes
> in. How does RabbitMQ distribute the 100 messages across the two workers, and what happens if one
> worker is on a machine that's twice as fast as the other — does load balance evenly, or does the
> faster worker end up doing more?"

(Expected direction: RabbitMQ round-robins by default, but `basic_qos(prefetch_count=1)` combined with
manual acks means a faster worker naturally pulls more messages sooner — it acks and asks for the next
one faster — so throughput self-balances toward the faster consumer, unlike naive round-robin with no
prefetch limit.)
