"""
Unit test for Database connectivity and session initialization.
"""

from sqlalchemy import text
from app.db.session import check_database_connection, SessionLocal


def test_database_connection():
    """Verifies that the database engine can successfully execute a test query."""
    assert check_database_connection() is True


def test_database_session_lifecycle():
    """Verifies that a session can be instantiated and closed cleanly."""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()
