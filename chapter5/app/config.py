from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Chapter 5 - Dependency Injection"
    jwt_secret: str = "dev-secret-change-me"
    debug: bool = True

@lru_cache
def get_settings() -> Settings:
    """
    lru_cache turns this into a singleton dependency: FastAPI calls get_settings()
    on every request that depends on it, but the cache means the Settings object
    is only actually constructed once per process.
    """
    return Settings()
