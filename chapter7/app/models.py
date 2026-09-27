from enum import Enum

class Role(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"

USERS = {
    "alice@example.com": {"email": "alice@example.com", "role": Role.admin, "team": "core"},
    "bob@example.com":   {"email": "bob@example.com",   "role": Role.manager, "team": "core"},
    "carol@example.com": {"email": "carol@example.com", "role": Role.user,   "team": "core"},
    "dave@example.com":  {"email": "dave@example.com",  "role": Role.user,   "team": "other"},
}

PROFILES = {u: {"email": u, "bio": f"Hi, I'm {u.split('@')[0]}"} for u in USERS}
