"""
The core testing pattern for a DB-backed FastAPI app: override get_db to point
at an isolated in-memory SQLite database instead of the real Postgres, using
FastAPI's dependency_overrides. Tests never touch a real database, run in
milliseconds, and each test gets a clean slate.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import Base, get_db
from app.auth import get_current_user

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def auth_headers(email: str) -> dict:
    return {"X-User-Email": email}
