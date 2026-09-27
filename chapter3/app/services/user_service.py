"""
Service layer: business rules and orchestration. Knows nothing about HTTP
(no Request/Response objects here) and nothing about how data is persisted
(that's the repository's job). This is what makes services unit-testable
without spinning up FastAPI or a database.
"""
from app.repositories.user_repository import UserRepository
from app.models.user import User


class DuplicateEmailError(Exception):
    pass


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def register_user(self, name: str, email: str) -> User:
        if self._repo.find_by_email(email) is not None:
            raise DuplicateEmailError(f"Email {email} already registered")
        return self._repo.add(name, email)

    def get_user(self, user_id: int) -> User | None:
        return self._repo.get(user_id)

    def list_users(self) -> list[User]:
        return self._repo.list()
