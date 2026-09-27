from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Chapter 3 - Layered Architecture"
    env: str = "development"

settings = Settings()
