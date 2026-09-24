"""REACTRA V2 — Custody Transfer Service.
Handles officer-recorded chain-of-custody handoffs for sealed evidence.
"""

import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session

from app.db.models.custody import CustodyEvent
from app.db.models.audit import AuditEvent
from app.domain.identifiers import generate_event_id
from app.domain.state_machine import SessionState
from app.repositories.session_repository import SessionRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.custody_repository import CustodyRepository
from app.repositories.audit_repository import AuditRepository
from app.schemas.custody import CustodyCreateRequest, CustodyEventResponse


class CustodyService:
    """Coordinates recording and retrieval of append-only custody events."""

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.custody_repo = CustodyRepository(db)
        self.audit_repo = AuditRepository(db)

    def record_custody_handoff(
        self, session_id: str, req: CustodyCreateRequest
    ) -> CustodyEventResponse:
        """
        Records an officer-entered physical custody transfer event for a sealed test session.
        Enforces that session must be sealed, creates immutable custody record, and appends to audit stream.
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session.status not in (SessionState.EVIDENCE_SEALED.value, SessionState.COMPLETED.value):
            raise ValueError(
                f"Custody handoff can only be recorded for sealed evidence (Current state: '{session.status}')."
            )

        evidence = self.evidence_repo.get_by_session_id(session_id)
        if not evidence:
            raise ValueError(f"No sealed evidence envelope found for session '{session_id}'.")

        now_utc = datetime.now(timezone.utc)
        custody_id = f"CUST-{session_id[-8:]}-{int(now_utc.timestamp() * 1000)}-{uuid.uuid4().hex[:4].upper()}"

        custody_event = CustodyEvent(
            id=custody_id,
            evidence_id=evidence.id,
            session_id=session_id,
            sender_operator_id=session.operator_id or "UNKNOWN-OFFICER",
            receiver_name=req.receiver_name.strip(),
            receiver_agency=req.receiver_agency.strip(),
            receiver_badge_or_id=req.receiver_badge_or_id.strip(),
            package_seal_verified=req.package_seal_verified,
            notes=req.notes.strip() if req.notes else None,
            transferred_at_utc=now_utc,
            created_at_utc=now_utc,
        )

        persisted = self.custody_repo.create(custody_event)

        # Append to Audit Log
        self.audit_repo.append(
            AuditEvent(
                event_id=generate_event_id(),
                test_id=session_id,
                event_type="CUSTODY_HANDOFF_RECORDED",
                from_state=session.status,
                to_state=session.status,
                actor_id=session.operator_id or "Evidence Custodian",
                device_enrollment_id=session.device_enrollment_id or "DEV-OFFLINE-LOCAL",
                event_payload={
                    "custody_event_id": custody_id,
                    "evidence_id": evidence.id,
                    "receiver_name": req.receiver_name,
                    "receiver_agency": req.receiver_agency,
                    "receiver_badge_or_id": req.receiver_badge_or_id,
                    "package_seal_verified": req.package_seal_verified,
                    "transferred_at_utc": now_utc.isoformat(),
                },
                event_timestamp_utc=now_utc,
            )
        )
        self.db.commit()

        return CustodyEventResponse(
            id=persisted.id,
            evidence_id=persisted.evidence_id,
            session_id=persisted.session_id,
            sender_operator_id=persisted.sender_operator_id,
            receiver_name=persisted.receiver_name,
            receiver_agency=persisted.receiver_agency,
            receiver_badge_or_id=persisted.receiver_badge_or_id,
            package_seal_verified=persisted.package_seal_verified,
            notes=persisted.notes,
            transferred_at_utc=persisted.transferred_at_utc.isoformat(),
        )

    def get_custody_history(self, session_id: str) -> List[CustodyEventResponse]:
        """Retrieves all custody handoff records for a session."""
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        events = self.custody_repo.list_by_session_id(session_id)
        return [
            CustodyEventResponse(
                id=evt.id,
                evidence_id=evt.evidence_id,
                session_id=evt.session_id,
                sender_operator_id=evt.sender_operator_id,
                receiver_name=evt.receiver_name,
                receiver_agency=evt.receiver_agency,
                receiver_badge_or_id=evt.receiver_badge_or_id,
                package_seal_verified=evt.package_seal_verified,
                notes=evt.notes,
                transferred_at_utc=evt.transferred_at_utc.isoformat(),
            )
            for evt in events
        ]
