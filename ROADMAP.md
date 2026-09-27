# Roadmap

## Dependency graph

```mermaid
flowchart TD
    C1[Ch1 FastAPI Fundamentals] --> C2[Ch2 REST API Design]
    C2 --> C3[Ch3 Project Architecture]
    C3 --> C4[Ch4 Database Integration]
    C4 --> C5[Ch5 Dependency Injection]
    C5 --> C6[Ch6 JWT Authentication]
    C6 --> C7[Ch7 Authorization / RBAC]
    C7 --> C8[Ch8 Middleware]
    C8 --> C9[Ch9 Error Handling]
    C9 --> C10[Ch10 Rate Limiting]
    C10 --> C11[Ch11 Async FastAPI]
    C11 --> C12[Ch12 Caching]
    C12 --> C13[Ch13 Message Queues: Concepts]
    C13 --> C14[Ch14 RabbitMQ]
    C13 --> C15[Ch15 Kafka]
    C14 --> C16[Ch16 Background Jobs]
    C15 --> C16
    C16 --> C17[Ch17 Monolith Architecture]
    C17 --> C18[Ch18 Microservices]
    C18 --> C19[Ch19 Monolith vs Microservices]
    C19 --> C20[Ch20 Scalability]
    C20 --> C21[Ch21 Resilience]
    C21 --> C22[Ch22 Observability]
    C22 --> C23[Ch23 Testing]
    C23 --> C24[Ch24 Security]
    C24 --> C25[Ch25 Production Deployment]
    C25 --> FP[Final Project: Order Management Platform]
```

## Why this order

- **1-3 (Fundamentals → REST → Architecture)**: you need a mental model of a request's full journey and
  a defensible project layout before anything else makes sense. Skipping straight to auth or queues on
  top of a messy `main.py` teaches bad habits that compound.
- **4-5 (Database → DI)**: DI is taught right after the database because `get_db()` is the dependency
  that makes everything downstream (auth, services, tests) composable.
- **6-9 (Auth → Authz → Middleware → Errors)**: these four are the "cross-cutting concerns" cluster —
  each one wraps around every request, so they're taught together.
- **10-12 (Rate limiting → Async → Caching)**: all three are about *protecting and speeding up* a
  single service before we introduce other services.
- **13-16 (Queues)**: once one service is solid, we introduce talking to *other* things asynchronously.
- **17-19 (Monolith → Microservices → Comparison)**: architecture decisions only make sense once you've
  felt the pain a modular monolith solves and the pain it eventually creates.
- **20-22 (Scale → Resilience → Observability)**: you cannot scale or harden a system you can't observe,
  so observability is deliberately taught last in that trio, once you know what's worth measuring.
- **23-25 (Testing → Security → Deployment)**: production readiness, done last on purpose — security and
  deployment decisions are much clearer once you've built and broken the system yourself.

## Suggested pace

| Weeks | Chapters | Milestone |
|-------|----------|-----------|
| 1 | 1-3 | Working CRUD API with a clean layered structure |
| 2 | 4-7 | Postgres-backed API with JWT auth + RBAC |
| 3 | 8-12 | Production-grade single service: middleware, errors, rate limits, caching |
| 4 | 13-16 | Same service now emits and consumes events |
| 5 | 17-19 | Can argue monolith-vs-microservices with real trade-offs, not slogans |
| 6 | 20-22 | Can explain how the system scales and what happens when a dependency dies |
| 7 | 23-25 | Tested, secured, deployable |
| 8 | Final project | Evolve one system through 6 real architecture versions |
