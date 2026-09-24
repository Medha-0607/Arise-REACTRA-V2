"""Database persistence foundation and models."""
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import engine, SessionLocal, get_db, check_database_connection
import app.db.models  # Ensures all ORM models are registered on Base.metadata

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "engine",
    "SessionLocal",
    "get_db",
    "check_database_connection",
]
