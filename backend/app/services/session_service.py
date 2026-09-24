"""
Authoritative Session Service for REACTRA V2.
Encapsulates session lifecycle management, transition validation, and audit recording.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models.session import TestSession
from app.db.models.timing import ReactionTiming
from app.db.models.measurement import MeasurementResult
from app.db.models.procedural import ProceduralContext
from app.db.models.audit import AuditEvent
from app.repositories.session_repository import SessionRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.profile_repository import ProfileRepository
from app.domain.state_machine import SessionState, SessionStateMachine, InvalidTransitionError
from app.domain.identifiers import generate_session_id, generate_event_id
from app.schemas.session import SessionCreateRequest, SessionTransitionRequest


class SessionNotFoundError(Exception):
    """Raised when a requested session is not found in local persistence."""
    pass


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditRepository(db)
        self.profile_repo = ProfileRepository(db)

    def create_session(self, req: SessionCreateRequest) -> TestSession:
        """
        Creates a new test session in DRAFT state, binds immutable assay profile metadata,
        instantiates child record shells, and records initial audit event.
        """
        session_id = generate_session_id()
        now_utc = datetime.now(timezone.utc)

        if req.is_demo_mode:
            resolved_device_id = req.device_enrollment_id or "DEV-OFFLINE-LOCAL"
        else:
            if not req.device_enrollment_id:
                raise ValueError("Normal field/production session requires an explicit device_enrollment_id.")
            resolved_device_id = req.device_enrollment_id

        # 1. Instantiate Core TestSession
        session = TestSession(
            id=session_id,
            case_id=req.case_id,
            event_id=req.event_id,
            operator_id=req.operator_id,
            field_officer_name=req.field_officer_name,
            field_officer_designation=req.field_officer_designation,
            police_station_jurisdiction=req.police_station_jurisdiction,
            assay_profile_id=req.assay_profile_id,
            assay_profile_version=req.assay_profile_version,
            status=SessionState.DRAFT.value,
            capture_mode=req.capture_mode.value,
            gps_status=req.gps_status.value,
            latitude=req.latitude,
            longitude=req.longitude,
            location_accuracy=req.location_accuracy,
            location_description=req.location_description,
            sync_state="LOCAL_ONLY",
            device_enrollment_id=resolved_device_id,
            created_at_utc=now_utc,
            updated_at_utc=now_utc,
        )

        # 2. Instantiate Child Record Shells
        timing = ReactionTiming(
            test_id=session_id,
            reaction_started_at_utc=None,
            capture_timestamp_utc=None,
            capture_elapsed_seconds=None,
            timer_source="MONOTONIC_LOCAL",
            kinetic_window_status="IN_WINDOW",
            t_min_seconds_snapshot=15.0,
            t_max_seconds_snapshot=60.0,
        )

        measurement = MeasurementResult(
            test_id=session_id,
            quality_status="PENDING",
            algorithm_version="v1.0.0",
            model_version="v1.0.0",
        )

        procedural = ProceduralContext(
            test_id=session_id,
            search_context_type=req.search_context_type,
            panchnama_memo_ref_no=req.panchnama_memo_ref_no,
            officer_notes=req.officer_notes,
        )

        # 3. Persist atomically
        created_session = self.session_repo.create(session, timing, measurement, procedural)

        # 4. Append Initial Creation Audit Event
        self._record_audit_event(
            session_id=session_id,
            event_type="SESSION_CREATED",
            from_state=None,
            to_state=SessionState.DRAFT.value,
            actor_id=req.operator_id,
            payload={
                "case_id": req.case_id,
                "profile_id": req.assay_profile_id,
                "profile_version": req.assay_profile_version,
                "capture_mode": req.capture_mode.value,
            },
        )

        return created_session

    def get_session(self, session_id: str) -> TestSession:
        """Retrieves session by ID or raises SessionNotFoundError."""
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")
        return session

    def list_sessions(
        self,
        skip: int = 0,
        limit: int = 50,
        operator_id: Optional[str] = None,
        status: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> List[TestSession]:
        """Lists test sessions from local repository."""
        return self.session_repo.list_sessions(skip=skip, limit=limit, operator_id=operator_id, status=status, case_id=case_id)

    def transition_session(self, session_id: str, req: SessionTransitionRequest) -> TestSession:
        """
        Executes a validated domain state transition.
        Rejects invalid transitions and logs an immutable audit event.
        """
        session = self.get_session(session_id)
        current_state = SessionState(session.status)
        target_state = req.target_state

        # Validate transition using Domain State Machine
        SessionStateMachine.validate_transition(
            current_state=current_state,
            target_state=target_state,
            quality_passed=req.quality_passed,
        )

        # Apply state update
        previous_status = session.status
        session = self.session_repo.update_status(session, target_state.value)

        # Update child measurement shell if transitioning out of quality checking
        if target_state == SessionState.READY_FOR_CLASSIFICATION and session.measurement:
            session.measurement.quality_status = "PASS"
            self.db.commit()
        elif target_state == SessionState.VALIDATION_FAILED and session.measurement:
            session.measurement.quality_status = "FAIL"
            self.db.commit()

        # Record Transition Audit Event
        actor = req.actor_id or session.operator_id
        self._record_audit_event(
            session_id=session_id,
            event_type="STATE_TRANSITION",
            from_state=previous_status,
            to_state=target_state.value,
            actor_id=actor,
            payload=req.event_payload or {},
        )

        return session

    def get_timeline(self, session_id: str) -> List[AuditEvent]:
        """Retrieves chronological audit trail for a session."""
        # Ensure session exists
        self.get_session(session_id)
        return self.audit_repo.list_by_session(session_id)

    def _record_audit_event(
        self,
        session_id: str,
        event_type: str,
        from_state: Optional[str],
        to_state: Optional[str],
        actor_id: str,
        payload: Dict[str, Any],
    ) -> AuditEvent:
        """Internal helper for logging immutable audit events."""
        event = AuditEvent(
            event_id=generate_event_id(),
            test_id=session_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            actor_id=actor_id,
            device_enrollment_id="DEV-OFFLINE-LOCAL",
            event_payload=payload,
            event_timestamp_utc=datetime.now(timezone.utc),
        )
        return self.audit_repo.append(event)
