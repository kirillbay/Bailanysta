"""Test DB setup — isolated SQLite file per run (PostgreSQL in prod).

We use a temporary SQLite DB for unit tests so CI/local without Docker still passes.
PostgreSQL-specific checks (e.g. UUID, now()) are exercised via migration SQL inspection
and via integration note: full PG constraints are validated on deployed Postgres.

Alembic migration 001 is compatible with SQLite for the tests (UUID stored as BLOB/CHAR).
"""

import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
import app.models  # noqa: F401 — register users


TEST_DB_PATH = Path(__file__).parent / ".test_bailanysta.db"


@pytest.fixture(scope="session")
def test_engine():
    # File-based SQLite so multiple connections see same DB (StaticPool would also work)
    # Use check_same_thread=False for thread safety in tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass


@pytest.fixture()
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
