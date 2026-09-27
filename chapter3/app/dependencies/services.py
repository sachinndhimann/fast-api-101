"""
Dependency wiring: this is the seam FastAPI's Depends() plugs into (chapter 5
goes deep on this). A single shared repository instance backs the service for
the lifetime of the process -- in a real app the repository would instead
depend on a per-request DB session.
"""
from functools import lru_cache
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository()

def get_user_service() -> UserService:
    return UserService(get_user_repository())
