from fastapi import Depends, Header, HTTPException, status
from app.config import Settings, get_settings

FAKE_TOKENS = {"token-alice": {"id": 1, "name": "Alice", "role": "admin"},
               "token-bob": {"id": 2, "name": "Bob", "role": "user"}}


def get_current_user(
    authorization: str | None = Header(None),
    settings: Settings = Depends(get_settings),  # NESTED dependency
):
    """
    A dependency that itself depends on another dependency (get_settings).
    FastAPI resolves the whole graph automatically and only computes each
    dependency once per request, even if multiple things need `settings`.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ")
    user = FAKE_TOKENS.get(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def require_admin(user: dict = Depends(get_current_user)):
    """Depends on get_current_user -- another nested dependency, this time enforcing a rule."""
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
