"""Database configuration and session management"""

import logging
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlmodel import SQLModel
from sqlalchemy.pool import NullPool

from app.config import settings

logger = logging.getLogger(__name__)

# Use SQLModel as base — SQLModel.metadata is shared across all models
Base = SQLModel


# Create async engine
engine_kwargs = {
    "echo": settings.echo_sql,
    "connect_args": {"timeout": 30, "command_timeout": 30},
}

# Configure pool based on environment
if settings.environment == "development":
    engine_kwargs["poolclass"] = NullPool  # No pooling for dev
else:
    # Production: use default QueuePool with size controls
    engine_kwargs["pool_size"] = settings.database_pool_size
    engine_kwargs["max_overflow"] = settings.database_max_overflow

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    **engine_kwargs
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to inject async database session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        # This is used with Alembic migrations in production
        # For development/testing, you can use Base.metadata.create_all(conn)
        # But we'll use Alembic for proper migrations
        logger.info("Database initialized")


async def dispose_db():
    """Dispose database connection pool"""
    await engine.dispose()
    logger.info("Database connections disposed")
