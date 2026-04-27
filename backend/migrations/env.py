"""Alembic environment configuration for database migrations"""

import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Import all models here for autogenerate to find them
from app.database import Base
from app.models import *  # noqa

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

# Get DATABASE_URL from app config
import os
from pathlib import Path
import sys

# Add parent directory to path so we can import app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (script only)"""
    
    url = settings.database_url.replace("postgresql+asyncpg", "postgresql")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper for running migrations"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with real DB connection)"""
    
    # Convert async URL to sync for Alembic
    url = settings.database_url.replace("postgresql+asyncpg", "postgresql")
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url
    
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        echo=settings.echo_sql,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()


if context.is_offline_mode():
    logger.info("Running migrations in 'offline' mode")
    run_migrations_offline()
else:
    logger.info("Running migrations in 'online' mode")
    asyncio.run(run_migrations_online())
