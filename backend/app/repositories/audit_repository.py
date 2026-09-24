"""
Repository for Audit Events (Append-Only Log).
"""

from typing import List
from sqlalchemy.orm import Session
from app.db.models.audit import AuditEvent


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def append(self, event: AuditEvent) -> AuditEvent:
        """Appends a new immutable audit record to the local log."""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_by_session(self, session_id: str) -> List[AuditEvent]:
        """Retrieves chronological audit trail for a session."""
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.test_id == session_id)
            .order_by(AuditEvent.event_timestamp_utc.asc())
            .all()
        )
