# fastapi-101

A hands-on backend engineering course built as a runnable repository, not a tutorial you read once and forget.

You already know Python and have backend experience, so this skips basic syntax and goes straight at
**how backend systems actually work**: API design, async internals, auth, middleware, rate limiting,
caching, queues, monolith-vs-microservices trade-offs, scalability, resilience, observability, testing,
security and production deployment.

## How this repo is organized

```
fastapi-101/
├── chapter1 .. chapter25/   one topic each, same shape:
│   ├── README.md            concept -> mental model -> diagram -> implementation -> production notes
│   ├── docs/                deeper notes, diagrams, decision tables
│   ├── app/                 the runnable FastAPI app for this chapter
│   ├── scripts/             curl/httpie scripts to exercise the app
│   └── exercises/           a task for you + an interview-style scenario
├── workflows/               16 "how do I actually do X" runbooks
└── final-project/           an Order Management Platform evolved through 6 architecture versions
```

Every chapter README follows the same teaching loop:

```
CONCEPT → MENTAL MODEL → DIAGRAM → MINIMAL EXAMPLE → REALISTIC EXAMPLE
        → COMMON MISTAKES → PRODUCTION CONSIDERATIONS → EXERCISE → INTERVIEW SCENARIO
```

Chapters 1-13 are meant to be worked through in order — each app builds on ideas from the last.
Chapters 14-25 branch out into infrastructure and architecture topics that don't require the earlier
chapter's code specifically, but do assume you've internalized the FastAPI fundamentals from chapters 1-9.

## Prerequisites

- Python 3.11+
- Docker + Docker Compose (for Postgres, Redis, RabbitMQ, Kafka)
- Basic SQL

## Getting started

```bash
make install          # creates .venv, installs requirements.txt
cp .env.example .env
make up                # starts postgres, redis, rabbitmq
make run CHAPTER=chapter1
# visit http://localhost:8000/docs
```

## The learning path

See `ROADMAP.md` for the full dependency graph. Short version:

```
Fundamentals → REST Design → Architecture → Database → DI
   → Auth (JWT) → Authorization → Middleware → Errors
   → Rate Limiting → Async → Caching → Queues (Rabbit/Kafka)
   → Monolith → Microservices → Scalability → Resilience
   → Observability → Testing → Security → Production Deployment
   → Final Project (6 architecture evolutions)
```

## Chapter index

| # | Chapter | Runs against |
|---|---------|---------------|
| 1 | FastAPI Fundamentals | none |
| 2 | REST API Design | none (design guide) |
| 3 | Project Architecture | none |
| 4 | Database Integration | postgres |
| 5 | Dependency Injection | postgres |
| 6 | JWT Authentication | postgres |
| 7 | Authorization (RBAC) | postgres |
| 8 | Middleware | none |
| 9 | Error Handling | none |
| 10 | Rate Limiting | redis |
| 11 | Async FastAPI | none |
| 12 | Caching | redis, postgres |
| 13 | Message Queues (concepts) | none |
| 14 | RabbitMQ | rabbitmq |
| 15 | Kafka | kafka |
| 16 | Background Jobs (comparison) | none |
| 17 | Monolith Architecture | postgres |
| 18 | Microservices | postgres x2 |
| 19 | Monolith vs Microservices | none (decision guide) |
| 20 | Scalability | redis, postgres |
| 21 | Resilience | none |
| 22 | Observability | none |
| 23 | Testing | postgres |
| 24 | Security | postgres |
| 25 | Production Deployment | docker |

Each chapter is self-contained enough to run on its own — see that chapter's `README.md` for exact
setup steps.

## Non-negotiable rule of this course

Every chapter shows the failure mode before the fix. If you only ever see the happy path, you haven't
learned the trade-off — you've memorized a snippet.
