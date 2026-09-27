# Chapter 25 — Production Deployment

## Concept

Taking a FastAPI app from `uvicorn --reload` on a laptop to a containerized, process-managed,
health-checked, gracefully-deployable production service.

## Why it exists

Every chapter so far assumed a running app. This chapter is about the layer beneath: how the app
actually gets built, started, monitored, and safely replaced during a deploy without dropping requests
or losing in-flight work.

## Diagram — the path to production

```mermaid
flowchart LR
    Dev[Local: uvicorn --reload] --> Docker[Docker: multi-stage build]
    Docker --> CI[CI: test, build image]
    CI --> Registry[Push to image registry]
    Registry --> Deploy[Rolling deploy: k8s/orchestrator]
    Deploy --> LB[Load balancer routes by readiness]
```

## Docker — multi-stage build

`docker/Dockerfile` uses two stages: a `builder` stage installs dependencies into a virtualenv, and the
final stage copies **only** that virtualenv plus app code — no compilers, no pip cache, no build-time
files ship in the final image. It also runs as a **non-root user** (`appuser`) — a compromised
root-in-container process gives an attacker meaningfully more than a compromised non-root one, for zero
functional benefit to running as root.

## Uvicorn vs Gunicorn + Uvicorn workers

```bash
uvicorn main:app --reload                                              # dev: one process, auto-reload
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000   # prod
```

A single Python process is limited by the GIL for CPU-bound work and represents a single point of
failure — if it crashes, the whole service is down. Gunicorn manages multiple **worker processes**
(here, 4), each running its own Uvicorn event loop; a crash in one worker doesn't take down the others,
and you get real multi-core utilization that a single async process alone doesn't provide.

## Environment configuration and secrets

Configuration (this course's `.env.example` pattern, chapter 5's `Settings`) comes from environment
variables, injected by your deployment platform — never baked into the image. Secrets specifically
(DB passwords, JWT signing keys, API keys) belong in a secrets manager or your orchestrator's secret
store, not plain environment variables in a compose file committed to version control (note
`docker-compose.prod.yml` here references `${DATABASE_URL}` from the *environment*, not a hardcoded
value).

## Graceful shutdown

`app/main.py`'s `lifespan` context manager (FastAPI's modern replacement for `@app.on_event`) runs setup
before the app starts serving and teardown after it stops accepting new requests — verified above: the
startup log line fires before any request is served, and the shutdown line fires only after the
`TestClient`'s context exits.

In production, this pairs with Gunicorn's `--graceful-timeout`: on `SIGTERM` (what Kubernetes and most
orchestrators send before killing a pod), Gunicorn stops accepting *new* connections but lets in-flight
requests finish, up to the graceful timeout — this is what lets `/slow`'s 3-second request complete even
if a deploy's shutdown signal arrives partway through it, instead of being abruptly cut off.

## Health checks, migrations, horizontal scaling — tying it together

- **Health checks** (chapter 22): the Dockerfile's `HEALTHCHECK` and the compose file's `healthcheck:`
  both hit `/health` — this is what lets `docker ps` and orchestrators see container-level health
  directly, distinct from (but complementary to) Kubernetes-level liveness/readiness probes.
- **Database migrations** (chapter 4's Alembic): run as a **separate, explicit CI/CD step** (see
  `ci/github-actions-example.yml`), before new application code that depends on the new schema starts
  receiving traffic — never `Base.metadata.create_all()` in production.
- **Horizontal scaling** (chapter 20): the Dockerfile and compose config here assume statelessness is
  already correct — deploying more container replicas is meaningless (or actively harmful, per chapter
  20's demo) if the app still has in-memory state that breaks under multiple instances.

## Reverse proxy and load balancing

In most real deployments, Nginx/Envoy/a cloud load balancer sits in front of your Gunicorn/Uvicorn
processes, handling TLS termination, request buffering, and distributing traffic across container
replicas — this chapter's Dockerfile exposes plain HTTP on 8000, deliberately leaving TLS to that layer
rather than terminating it inside the app container.

## CI/CD

`ci/github-actions-example.yml` shows the shape: **test → build image → push → deploy**, each stage
gated on the previous succeeding (`needs: test` before building, `needs: build-and-push` before
deploying) — an image that hasn't passed tests should never reach a registry, let alone production. The
`deploy` job's comment calls out explicitly that a safe rolling deploy depends on both chapter 22's
readiness probes (so traffic only shifts to genuinely-ready new pods) and this chapter's graceful
shutdown (so old pods finish in-flight work) — missing either one means a rolling deploy silently drops
requests.

## Common mistakes

- Running the dev server (`uvicorn --reload`) in production — no multi-process worker management, and
  the file-watching overhead of `--reload` is pure waste in a static production image.
- No graceful shutdown handling — a deploy or pod eviction abruptly kills in-flight requests, and clients
  see connection resets instead of clean responses.
- Running database migrations automatically on app startup inside every replica — with multiple
  replicas starting simultaneously during a deploy, this can race and corrupt a migration; run migrations
  once, as a distinct step, before app instances start.
- Building a single-stage Docker image that includes compilers and build caches in the final image —
  larger attack surface, slower pulls, no functional benefit.

## Exercise

Extend `app/main.py`'s `lifespan` to actually open a real async SQLAlchemy engine (chapter 4) on startup
and dispose it on shutdown, storing it on `app.state` so routes can access it via a dependency. Confirm
via logging that disposal happens exactly once, even if the app receives multiple shutdown signals.

## Interview-style scenario

> "During a deploy, you notice a spike in 502 errors from your load balancer lasting about 10 seconds
> each time. Your readiness probes are configured correctly. What's the most likely remaining cause,
> and how does Gunicorn's `--graceful-timeout` setting relate to fixing it?"
