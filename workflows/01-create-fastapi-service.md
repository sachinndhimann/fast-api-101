# Workflow: Create a new FastAPI service

## Problem
You need to start a brand-new FastAPI service with a sane, production-oriented structure from commit one,
instead of a single `main.py` that will need painful restructuring later.

## Investigation
Decide up front: will this be a single-domain service (chapter 3's layered structure) or does it already
have multiple domains (chapter 17's per-domain modules)? Most new services start single-domain.

## Implementation
```bash
mkdir my-service && cd my-service
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi "uvicorn[standard]" pydantic-settings sqlalchemy asyncpg alembic pytest httpx
mkdir -p app/{api,schemas,models,services,repositories,dependencies,core,tests}
touch app/__init__.py app/{api,schemas,models,services,repositories,dependencies,core,tests}/__init__.py
```
Follow chapter 3's layering: routers in `api/`, request/response shapes in `schemas/`, DB tables in
`models/`, business rules in `services/`, storage access in `repositories/`, `Depends()` targets in
`dependencies/`.

## Testing
```bash
cat > app/main.py << 'PY'
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
PY
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
curl localhost:8000/health
```

## Validation
- `/docs` loads and shows the health endpoint.
- `pytest app/tests` runs (even with zero tests yet) without import errors.

## Production considerations
Set up `.env.example`, a `Dockerfile` (chapter 25), and a CI workflow (chapter 25's example) before the
first real feature lands — retrofitting these onto an already-growing codebase is more friction than
starting with them.
