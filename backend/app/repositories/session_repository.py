"""
Repository for Test Sessions and Child Entities.
Encapsulates all persistence operations for domain sessions.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.db.models.session import TestSession
from app.db.models.timing import ReactionTiming
from app.db.models.measurement import MeasurementResult
from app.db.models.procedural import ProceduralContext


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session: TestSession,
        timing: ReactionTiming,
        measurement: MeasurementResult,
        procedural: ProceduralContext,
    ) -> TestSession:
        """Persists a new test session and its associated child shells in an atomic transaction."""
        self.db.add(session)
        self.db.add(timing)
        self.db.add(measurement)
        self.db.add(procedural)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: str) -> Optional[TestSession]:
        """Retrieves session with full child entity relationships loaded."""
        return (
            self.db.query(TestSession)
            .options(
                joinedload(TestSession.timing),
                joinedload(TestSession.measurement),
                joinedload(TestSession.procedural_context),
                joinedload(TestSession.evidence),
                joinedload(TestSession.audit_events),
            )
            .filter(TestSession.id == session_id)
            .first()
        )

    def list_sessions(
        self,
        skip: int = 0,
        limit: int = 50,
        operator_id: Optional[str] = None,
        status: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> List[TestSession]:
        """Lists test sessions with optional filtering."""
        query = self.db.query(TestSession)
        if operator_id:
            query = query.filter(TestSession.operator_id == operator_id)
        if status:
            query = query.filter(TestSession.status == status)
        if case_id:
            query = query.filter(TestSession.case_id == case_id)
        return query.order_by(TestSession.created_at_utc.desc()).offset(skip).limit(limit).all()

    def update_status(self, session: TestSession, new_status: str) -> TestSession:
        """Updates the authoritative status of a session."""
        session.status = new_status
        self.db.commit()
        self.db.refresh(session)
        return session
