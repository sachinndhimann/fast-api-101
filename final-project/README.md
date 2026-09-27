# Final Project — Order Management Platform

A system evolved through 6 architecture versions, tying together every chapter in this course. Only
**V1** is implemented as running code here; V2-V6 are fully specified in `docs/evolution.md` as guided
exercises, each reusing a specific earlier chapter's code directly.

## What's implemented (V1: Modular Monolith)

```
app/
├── products/    # Product catalog: model, service, router
├── orders/      # Order creation: calls products + payments as plain function calls
├── payments/    # Payment charging: has ZERO knowledge of orders or products (chapter 17's discipline)
├── core/        # Shared database setup (chapter 4's pattern)
└── tests/       # Full-stack tests against an isolated in-memory SQLite DB (chapter 23's pattern)
```

## Run it

```bash
cd final-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
docker compose -f ../docker-compose.yml up -d postgres   # or skip and point DATABASE_URL at your own
cp ../.env.example .env
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

```bash
curl -X POST "localhost:8000/products?name=Widget&price_cents=999"
curl -X POST "localhost:8000/orders?product_id=1&quantity=2"
```

## Test it

```bash
PYTHONPATH=. pytest app/tests -v
```

Tests run against an isolated in-memory SQLite database (no Postgres required) using the
`dependency_overrides` pattern from chapter 23 — `test_full_order_flow` exercises the complete path
(create a product, order it, confirm payment succeeded and status is "paid"), and
`test_order_for_missing_product_fails` confirms the 404 path never reaches the payment step at all.

## Where to go from here

Open `docs/evolution.md` and work through V2 (caching) → V3 (RabbitMQ) → V4 (Kafka) → V5 (extract
Payments into its own service) → V6 (horizontal scale + resilience) — each one names exactly which
chapter's code to reuse and what specifically changes, why, and at what cost. This is the capstone: by
V6, you will have personally taken one system through every architectural stage this course covers, not
just read about each stage in isolation.
