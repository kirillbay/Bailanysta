"""Convenience re-export — `from app.database import Base, get_db`.

Spec allows `backend/app/database.py` or `backend/app/database/*`.
We keep both: dir package is source of truth, this file re-exports.
"""

from app.database.base import Base
from app.database.session import engine, SessionLocal, get_db, check_db_connection

__all__ = ["Base", "engine", "SessionLocal", "get_db", "check_db_connection"]
