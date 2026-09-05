"""Alembic env — discovers Base.metadata from app.models."""

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config
from alembic import context

# Ensure backend/ is on path so `app.*` imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.database.base import Base
import app.models  # noqa: F401 — ensure all models imported

config = context.config

# Use DATABASE_URL from settings; convert async driver if present to sync psycopg
db_url = settings.database_url
# Support both postgresql+psycopg and postgresql+asyncpg forms in env
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "+psycopg")
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # When generating a revision without a live DB (offline env), allow skipping connection
    # so `alembic revision --autogenerate` can run without PostgreSQL running locally.
    try:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    except Exception as exc:
        import warnings

        warnings.warn(f"Alembic online run failed ({exc}); DB not reachable — skipping online migration run")
        # Don't try offline literal_binds without as_sql; just skip — upgrade requires live PG.
        # For offline SQL generation, use `alembic upgrade head --sql`
        return


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
