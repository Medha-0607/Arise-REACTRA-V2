"""SQLAlchemy repository for EvidenceRecord queries."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.evidence import EvidenceRecord


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_session_id(self, session_id: str) -> Optional[EvidenceRecord]:
        return self.db.query(EvidenceRecord).filter(EvidenceRecord.test_id == session_id).first()

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceRecord]:
        return self.db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()

    def list_by_device(self, device_enrollment_id: str) -> List[EvidenceRecord]:
        return (
            self.db.query(EvidenceRecord)
            .filter(EvidenceRecord.device_enrollment_id == device_enrollment_id)
            .order_by(EvidenceRecord.sealed_at_utc.asc(), EvidenceRecord.id.asc())
            .all()
        )
