"""Repository for Custody Transfer Events."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.custody import CustodyEvent


class CustodyRepository:
    """Encapsulates database operations for append-only CustodyEvent entities."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, custody_id: str) -> Optional[CustodyEvent]:
        """Fetches a custody event by its unique primary key."""
        return self.db.query(CustodyEvent).filter(CustodyEvent.id == custody_id).first()

    def list_by_session_id(self, session_id: str) -> List[CustodyEvent]:
        """Lists all custody transfer events recorded for a given session, ordered chronologically."""
        return (
            self.db.query(CustodyEvent)
            .filter(CustodyEvent.session_id == session_id)
            .order_by(CustodyEvent.transferred_at_utc.asc())
            .all()
        )

    def create(self, custody_event: CustodyEvent) -> CustodyEvent:
        """Persists a new custody event. Append-only."""
        self.db.add(custody_event)
        self.db.commit()
        self.db.refresh(custody_event)
        return custody_event
