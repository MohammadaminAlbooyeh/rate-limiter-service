"""Alembic migrations environment configuration for the Rate Limiter Service.

This configures Alembic to work with our async SQLAlchemy setup.
For async engines, we use run_async() to execute migrations.
"""
import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Alembic Config object
config = context.config

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect schema changes
from backend.models.database import Base
import backend.models.models  # noqa: F401 – registers all tables on Base.metadata

target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from environment or config fallback."""
    return os.environ.get(
        "DATABASE_URL",
        config.get_main_option("sqlalchemy.url"),
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without connecting)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper to run migrations on a given connection."""
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with an async engine."""
    url = get_url()
    connectable = create_async_engine(url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode, handling sync/async engines."""
    url = get_url()
    if url.startswith("sqlite"):
        # SQLite uses aiosqlite – use async connection
        asyncio.run(run_async_migrations())
    elif url.startswith("postgresql"):
        if "+asyncpg" in url or "+aiosqlite" in url:
            asyncio.run(run_async_migrations())
        else:
            # Sync fallback for non-async URLs
            from sqlalchemy import create_engine
            connectable = create_engine(url, poolclass=pool.NullPool)
            with connectable.connect() as connection:
                do_run_migrations(connection)
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
