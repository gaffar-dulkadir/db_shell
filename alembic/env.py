"""
Alembic environment configuration for Chat Marketplace Service
"""

import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Add src to Python path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datalayer.model.sqlalchemy_models import Base
from config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load our application config
app_config = Config()

# Override the sqlalchemy.url with our configuration
config.set_main_option('sqlalchemy.url', app_config.postgres_sync_url)

# Set environment variables for connection string interpolation
os.environ.setdefault('POSTGRES_HOST', app_config.postgres_host)
os.environ.setdefault('POSTGRES_PORT', str(app_config.postgres_port))
os.environ.setdefault('POSTGRES_DB', app_config.postgres_db)
os.environ.setdefault('POSTGRES_USER', app_config.postgres_user)
os.environ.setdefault('POSTGRES_PASSWORD', app_config.postgres_password)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Include schemas in migration
        include_schemas=True,
        # Version table schema
        version_table_schema='public'
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with database connection"""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        # Include schemas in migration
        include_schemas=True,
        # Version table schema
        version_table_schema='public',
        # Compare types for better migrations
        compare_type=True,
        # Compare server defaults
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()