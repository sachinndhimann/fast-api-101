# Order Management Platform — Architecture Evolution, V1 through V6

This document walks through evolving one system across 6 versions. **Only V1 is implemented as running
code** in `app/` (a modular monolith) — it's the foundation every later version builds from. V2-V6 are
specified in full detail (what changes, why, what complexity it adds, what trade-off it costs) so you can
implement each one yourself as an exercise, reusing the chapters this course already built:

- V2 reuses chapter 4 (database) + chapter 12 (caching)
- V3 reuses chapter 14 (RabbitMQ) + chapter 16 (background jobs)
- V4 reuses chapter 15 (Kafka)
- V5 reuses chapter 18 (microservices) + chapter 19 (the decision framework)
- V6 reuses chapter 20 (scalability) + chapter 21 (resilience)

For each version: **why** are we changing, **what problem** does the current version have, **what
complexity** are we introducing, **what trade-off** are we making.

---

## V1 — Simple FastAPI Monolith (implemented in `app/`)

**What it is**: `Products`, `Orders`, `Payments` as modules in one process (chapter 17's pattern),
sharing one database, `OrderService` calling `ProductService` and `payments.charge()` as plain Python
function calls.

**Why start here**: fastest to build, easiest to reason about, real ACID transactions across modules for
free, and — critically — clean module boundaries from day one (`payments` has zero knowledge of `orders`
or `products`) so every later evolution has a real seam to extract along.

Run it:
```bash
cd final-project
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
PYTHONPATH=. pytest app/tests -v
```

---

## V2 — Database + Redis

**Why we're changing**: as `GET /products` traffic grows, repeated reads of rarely-changing product
data are hitting Postgres unnecessarily on every request.

**What problem the current architecture has**: no caching layer; every product read is a full database
round trip, even for data that changes rarely.

**What complexity we're introducing**: a cache-aside layer (chapter 12) in front of `ProductService`,
plus cache invalidation logic on every write path.

**What trade-off we're making**: brief staleness windows (bounded by TTL) in exchange for reduced
database load and lower read latency. Also: one more piece of infrastructure (Redis) to run and monitor.

**Implementation sketch**: wrap `ProductService.get()` with chapter 12's `ProductCache`; invalidate on
`ProductService.create()` and any future update/delete methods.

---

## V3 — Background Workers + RabbitMQ

**Why we're changing**: order confirmation should trigger a notification (email/SMS), but sending it
synchronously inside `create_order` couples order-creation latency and availability to the notification
provider's latency and availability (chapter 13).

**What problem the current architecture has**: `OrderService.create_order` does everything synchronously
— if a notification provider is slow, order creation is slow too, even though nothing about "was payment
charged" depends on "was a notification sent."

**What complexity we're introducing**: a RabbitMQ broker (chapter 14), a producer call inside
`create_order` (replacing a hypothetical synchronous notification call), and a separate worker process
consuming `OrderCreated` events to send notifications, with retry and dead-letter handling.

**What trade-off we're making**: notification delivery is no longer synchronous or guaranteed-immediate
— a customer's confirmation email might arrive a few seconds after their order confirms on-screen, not
before. In exchange: order creation's availability/latency is now fully decoupled from the notification
provider's.

**Implementation sketch**: add a `notifications` module (chapter 17's exercise) whose router-facing
service publishes to RabbitMQ instead of sending directly; add `worker.py` per chapter 14.

---

## V4 — Event-Driven Components with Kafka

**Why we're changing**: beyond notifications, the business now wants analytics, a recommendation engine,
and a data warehouse sync — three more independent systems that all care about "orders happened," each
wanting to consume that stream at its own pace, potentially replaying history for a new analytics model.

**What problem the current architecture has**: RabbitMQ (V3) is well-suited to "get this one task done,"
but adding a 4th independent consumer of order events means either 4 separate RabbitMQ queues bound to the
same exchange (workable, but every new consumer type needs its own explicit queue) or — better fit here —
a Kafka topic that any number of independent consumer groups can read at their own pace, and that a
brand-new consumer (e.g. a recommendation model built next year) can replay from the beginning.

**What complexity we're introducing**: a Kafka cluster (chapter 15), publishing `OrderCreated` /
`OrderShipped` / `OrderCancelled` events keyed by `order_id`, and N independent consumer groups (one per
downstream system) each reading the same topic independently.

**What trade-off we're making**: more operational surface (Kafka is heavier to run and reason about than
RabbitMQ) in exchange for genuinely decoupled, replayable, multi-consumer event distribution — appropriate
specifically because we now have *multiple, independent* interested parties, which V3's RabbitMQ setup
solved for exactly *one* task.

**Implementation sketch**: reuse chapter 15's producer/consumer pattern directly, publishing from
`OrderService` after order state changes.

---

## V5 — Extract Selected Modules into Services

**Why we're changing**: Payments now needs PCI-compliance isolation and a dedicated on-call rotation
separate from the rest of the platform team (chapter 19's organizational-need trigger for extraction) —
a technical scaling need alone wasn't the reason; the compliance/ownership boundary was.

**What problem the current architecture has**: Payments code, deploys, and on-call are entangled with
Products/Orders — a Payments-only compliance audit or a Payments-only emergency deploy currently can't
happen without touching (or at least redeploying) the whole monolith.

**What complexity we're introducing**: Payments becomes its own service (chapter 18) with its own
database, its own deploy pipeline, and an HTTP API that `OrderService` now calls over the network instead
of importing directly — including a timeout and explicit handling for "Payments service unavailable"
(chapter 18's `503` pattern), which literally could not happen in V1-V4.

**What trade-off we're making**: real network latency and partial-failure handling where a function call
used to be instant and unconditionally reliable; loss of a single cross-module database transaction
(Order creation and Payment charge are no longer atomic together — see chapter 18's interview scenario
about exactly this).

**Implementation sketch**: follow workflow 13 (`workflows/13-monolith-to-microservices.md`) — because V1's
`payments.service.charge()` was already a single, clean function boundary (chapter 17's discipline paying
off here specifically), replacing its body with an HTTP call is a contained change, not a rewrite.

---

## V6 — Horizontally Scalable Architecture

**Why we're changing**: traffic has grown to the point where a single instance of the (now-partially
split) system can't keep up, and the business needs to survive traffic spikes and individual instance
failures without downtime.

**What problem the current architecture has**: single points of failure per service, and no capacity
headroom for traffic growth or spikes (a flash sale, a marketing campaign).

**What complexity we're introducing**: multiple instances per service behind load balancers (chapter 20),
which requires first auditing and removing any remaining in-process state (any local caches, in-memory
counters); connection pool sizing math across all instances (chapter 4); circuit breakers and retries on
every inter-service call (chapter 21, now especially important since V5 introduced real network calls
between Orders and Payments); and full observability (chapter 22) since debugging now spans multiple
instances of multiple services.

**What trade-off we're making**: meaningfully higher operational complexity (more moving parts to deploy,
monitor, and reason about) in exchange for the ability to survive both traffic growth and individual
component failures without a full-system outage — the payoff finally justifies the cost, specifically
because by this point the system has a proven, not hypothetical, need for it.

**Implementation sketch**: apply chapter 20's statelessness audit to every service from V1-V5; add
chapter 21's circuit breaker around the Orders → Payments HTTP call from V5; add chapter 22's
liveness/readiness endpoints and correlation-ID propagation across all services.

---

## The throughline

Notice what *didn't* change across all 6 versions: `payments.service.charge()`'s conceptual role (charge
an amount, return success/failure) stayed stable from V1 through V6, even as its implementation moved
from an in-process function (V1) to an HTTP-called separate service (V5) to a horizontally-scaled,
circuit-breaker-protected service (V6). That stability is the entire payoff of chapter 3's and chapter
17's insistence on clean layering and module boundaries from the very first version — the versions where
you *feel* that discipline paying off are V5 and V6, built on foundations laid in V1.
