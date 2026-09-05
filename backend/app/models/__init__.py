"""Import all models so Alembic sees them via Base.metadata."""

from app.models.user import User  # noqa: F401

__all__ = ["User"]
