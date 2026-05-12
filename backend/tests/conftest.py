"""Pytest configuration and fixtures

CRITICAL: Tests for the pedidos module require PostgreSQL because they use
SELECT FOR UPDATE, which is not supported by SQLite.

Use @pytest.mark.postgres to mark tests that require PostgreSQL.
These tests will be skipped if PostgreSQL is not available.
"""
import os
import sys
from pathlib import Path
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

# Load .env BEFORE importing app config
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "backend" / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    load_dotenv(override=True)

# Disable rate limiting for tests
from app.config import settings
settings.rate_limit_enabled = False

from app.main import app
from app.database import Base, get_db
from app.dependencies import get_uow
from app.middleware.rate_limiter import limiter
limiter.enabled = False

from tests.models import TestModel, UoWTestModel


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "postgres: marks tests that require PostgreSQL (SELECT FOR UPDATE not supported by SQLite)"
    )


def skip_if_no_postgres():
    """Skip if DATABASE_URL does not point to PostgreSQL."""
    db_url = os.environ.get("DATABASE_URL", "")
    return "postgresql" not in db_url and "postgres" not in db_url


# ── SQLite (memory) fixtures ────────────────────────────────────────────────────
# Used for unit tests and integration tests that don't need SELECT FOR UPDATE

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine using SQLite in-memory."""
    test_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        test_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def override_get_db(test_db_session):
    """Override get_db dependency for testing."""
    async def _override_get_db():
        yield test_db_session

    return _override_get_db


@pytest.fixture
async def client(override_get_db):
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()


# ── PostgreSQL fixtures ─────────────────────────────────────────────────────────
# REQUIRED for tests that use SELECT FOR UPDATE (pedidos module)

@pytest.fixture
async def pg_engine():
    """
    Create PostgreSQL test engine if DATABASE_URL points to PostgreSQL.

    This fixture is SESSION-scoped to reuse the same test database
    across all postgres-marked tests.
    """
    db_url = os.environ.get("DATABASE_URL", "")

    # Check if DATABASE_URL is PostgreSQL
    if "postgresql" not in db_url and "postgres" not in db_url:
        pytest.skip(
            "DATABASE_URL does not point to PostgreSQL. "
            "SELECT FOR UPDATE tests require PostgreSQL.",
            allow_module_level=True,
        )

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=30,
        max_overflow=2,
    )

    # Verify connection works
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"Cannot connect to PostgreSQL: {e}", allow_module_level=True)

    yield engine
    await engine.dispose()


@pytest.fixture
async def pg_session(pg_engine):
    """
    Create PostgreSQL session for SELECT FOR UPDATE tests.

    CRITICAL: This fixture is REQUIRED for testing stock validation
    in the pedidos module. SQLite does not support SELECT FOR UPDATE.

    Creates a session, cleans up test data, and yields it.
    Data must be committed by callers if it needs to be visible to the app.
    """
    async_session_maker = async_sessionmaker(
        pg_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Clean up test data using a dedicated connection
    async with pg_engine.begin() as conn:
        await conn.execute(text("""
            DELETE FROM historial_estado_pedido
            WHERE pedido_id IN (
                SELECT p.id FROM pedidos p
                WHERE p.usuario_id IN (
                    SELECT id FROM usuarios WHERE email LIKE '%@test.com'
                )
            )
        """))
        await conn.execute(text("""
            DELETE FROM detalles_pedido
            WHERE pedido_id IN (
                SELECT id FROM pedidos
                WHERE usuario_id IN (
                    SELECT id FROM usuarios WHERE email LIKE '%@test.com'
                )
            )
        """))
        await conn.execute(text("""
            DELETE FROM pedidos
            WHERE usuario_id IN (
                SELECT id FROM usuarios WHERE email LIKE '%@test.com'
            )
        """))
        await conn.execute(text("DELETE FROM usuarios WHERE email LIKE '%@test.com'"))

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def pg_client(pg_session):
    """
    Create test client that uses the shared pg_session.

    The pg_session provides the database session for both test setup
    and the HTTP client. Test data should be committed in the session
    before the client is used.
    """
    async def _override_get_db():
        yield pg_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()


# ── Auth helper fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def sync_client(client):
    """Create synchronous test client (deprecated, use async client)."""
    return client
