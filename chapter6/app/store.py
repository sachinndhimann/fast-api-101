"""In-memory user store + refresh-token allowlist, standing in for a real DB (chapter 4)."""
from app.security import hash_password

USERS: dict[str, dict] = {}          # email -> {email, hashed_password}
VALID_REFRESH_TOKENS: set[str] = set()  # allowlist -- lets us support logout/revocation (see notes)


def register(email: str, password: str) -> dict:
    if email in USERS:
        raise ValueError("Email already registered")
    user = {"email": email, "hashed_password": hash_password(password)}
    USERS[email] = user
    return user


def get_user(email: str) -> dict | None:
    return USERS.get(email)
