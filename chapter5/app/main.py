from fastapi import FastAPI, Depends
from app.config import Settings, get_settings
from app.db import get_db, FakeDBSession
from app.auth import get_current_user, require_admin

app = FastAPI(title="Chapter 5 - Dependency Injection")


@app.get("/settings-demo")
def settings_demo(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name, "debug": settings.debug}


@app.get("/db-demo")
def db_demo(db: FakeDBSession = Depends(get_db)):
    return {"session_open": not db.closed}


@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    """Try: curl -H 'Authorization: Bearer token-alice' localhost:8000/me"""
    return user


@app.get("/admin-only")
def admin_only(user: dict = Depends(require_admin)):
    """
    Dependency graph here: admin_only -> require_admin -> get_current_user -> get_settings.
    FastAPI resolves all four in order and injects the result at each level.
    """
    return {"message": f"Welcome, admin {user['name']}"}


# ---- Overriding dependencies for tests (see app/tests) ----
# app.dependency_overrides[get_current_user] = lambda: {"id": 99, "name": "Test", "role": "admin"}
