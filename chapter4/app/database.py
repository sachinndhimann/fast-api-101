import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://fastapi101:fastapi101@localhost:5432/fastapi101")

# pool_size / max_overflow matter in production: too small and requests queue
# waiting for a connection under load; too large and you can exhaust Postgres's
# own max_connections across all your app instances combined.
engine = create_async_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    """
    One session per request, always closed afterward (even on exception, via
    the `async with` context manager). This is the dependency chapter 5 builds
    on top of everywhere else in this course.
    """
    async with AsyncSessionLocal() as session:
        yield session
