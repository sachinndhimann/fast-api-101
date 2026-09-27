"""
Repository layer: the ONLY place that knows how users are actually stored.
Swap this file for a SQLAlchemy-backed one later and nothing above it changes.
"""
from app.models.user import User

class UserRepository:
    def __init__(self):
        self._db: dict[int, User] = {}
        self._next_id = 1

    def add(self, name: str, email: str) -> User:
        user = User(id=self._next_id, name=name, email=email)
        self._db[user.id] = user
        self._next_id += 1
        return user

    def get(self, user_id: int) -> User | None:
        return self._db.get(user_id)

    def list(self) -> list[User]:
        return list(self._db.values())

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._db.values() if u.email == email), None)
