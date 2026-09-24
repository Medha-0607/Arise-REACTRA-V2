import pytest
from app.main import app
from app.core.config import settings, EnvironmentType
from app.db.base import Base
from app.db.session import engine, SessionLocal

# Ensure test mode with isolated in-memory SQLite
settings.ENV = EnvironmentType.TESTING
settings.DEBUG = False
settings.DATABASE_URL = "sqlite:///:memory:"

# Create all tables on the in-memory test engine
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Provides a fresh database session for unit/integration tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
async def async_client():
    """Provides an asynchronous HTTP test client."""
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


