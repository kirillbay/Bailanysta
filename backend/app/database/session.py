"""Engine, SessionLocal, get_db dependency — SQLAlchemy 2.x sync style."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# SQLAlchemy 2.x: use psycopg driver for PostgreSQL
# Pool pre_ping protects against stale connections; echo only in debug
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug and not settings.is_production,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session, always closes."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Lightweight health probe: SELECT 1."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
