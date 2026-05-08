"""Pytest configuration and fixtures"""

import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.dependencies import get_uow
from tests.models import TestModel, UoWTestModel


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    # Use SQLite for tests (simpler, no external DB needed)
    # In production, use a test PostgreSQL database
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(test_db_session):
    """Override get_db dependency for testing"""
    async def _override_get_db():
        yield test_db_session
    
    return _override_get_db


@pytest.fixture
async def client(override_get_db):
    """Create test client with overridden dependencies"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(client):
    """Create synchronous test client (deprecated, use async client)"""
    return client
