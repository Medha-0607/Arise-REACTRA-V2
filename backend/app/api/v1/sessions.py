"""
Test Session REST API Endpoints for REACTRA V2.
Follows thin controller pattern; delegates business validation to Services.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.session_service import SessionService, SessionNotFoundError
from app.services.measurement_service import MeasurementService
from app.domain.state_machine import InvalidTransitionError
from app.scientific.image_io import ImageValidationError
from app.schemas.session import (
    SessionCreateRequest,
    SessionTransitionRequest,
    SessionSummaryResponse,
    SessionDetailResponse,
    SessionTimelineResponse,
    AuditEventResponse,
)
from app.schemas.measurement import (
    MeasurementExecuteRequest,
    MeasurementExecutionOutcomeResponse,
)
from app.schemas.classifier import ClassificationResponse
from app.schemas.evidence import EvidenceSealResponse
from app.schemas.procedural import (
    ProceduralContextResponse,
    ProceduralUpdateRequest,
    ReferralSummaryResponse,
)
from app.schemas.custody import CustodyCreateRequest, CustodyEventResponse
from app.schemas.referral import ReferralExportResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    req: SessionCreateRequest,
    db: Session = Depends(get_db),
) -> SessionDetailResponse:
    """Initializes a new presumptive test session in DRAFT state."""
    service = SessionService(db)
    session = service.create_session(req)
    return service.get_session(session.id)


@router.get("", response_model=List[SessionSummaryResponse])
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    operator_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    case_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[SessionSummaryResponse]:
    """Lists local test sessions with optional filtering."""
    service = SessionService(db)
    return service.list_sessions(skip=skip, limit=limit, operator_id=operator_id, status=status_filter, case_id=case_id)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionDetailResponse:
    """Retrieves full details and child shells for a specific test session."""
    service = SessionService(db)
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{session_id}/transition", response_model=SessionDetailResponse)
async def transition_session_state(
    session_id: str,
    req: SessionTransitionRequest,
    db: Session = Depends(get_db),
) -> SessionDetailResponse:
    """
    Executes a domain state transition for a test session.
    Rejects invalid transitions and enforces quality gating constraints.
    """
    service = SessionService(db)
    try:
        service.transition_session(session_id, req)
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_STATE_TRANSITION",
                "current_state": e.current_state.value,
                "target_state": e.target_state.value,
                "reason": e.reason,
            },
        )


@router.get("/{session_id}/timeline", response_model=SessionTimelineResponse)
async def get_session_timeline(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionTimelineResponse:
    """Retrieves the chronological audit event stream for a session."""
    service = SessionService(db)
    try:
        session = service.get_session(session_id)
        events = service.get_timeline(session_id)
        return SessionTimelineResponse(
            session_id=session.id,
            current_status=session.status,
            events=[AuditEventResponse.model_validate(e) for e in events],
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{session_id}/measure", response_model=MeasurementExecutionOutcomeResponse)
async def measure_session_capture(
    session_id: str,
    req: MeasurementExecuteRequest,
    db: Session = Depends(get_db),
) -> MeasurementExecutionOutcomeResponse:
    """
    Executes the Adaptive Capture Guard and scientific measurement pipeline.
    Validates optical quality, normalizes reference card, performs color calibration,
    and extracts reaction well CIE L*a*b* coordinates.
    
    If quality verification passes: transitions session to READY_FOR_CLASSIFICATION
    and returns a ValidatedMeasurement.
    If quality verification fails: transitions session to VALIDATION_FAILED and
    returns structured quality diagnostics with NO ValidatedMeasurement.
    """
    service = MeasurementService(db)
    try:
        return service.process_capture_and_measure(
            session_id=session_id,
            image_source=req.image_base64,
            provenance=req.provenance,
            elapsed_seconds=req.elapsed_seconds,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ImageValidationError, InvalidTransitionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/classify", response_model=ClassificationResponse, status_code=status.HTTP_200_OK)
async def classify_session_measurement(
    session_id: str,
    db: Session = Depends(get_db),
) -> ClassificationResponse:
    """
    Executes profile-bound presumptive colorimetric classification on the ValidatedMeasurement.
    Transitions session to CLASSIFIED (or REVIEW_REQUIRED if inconclusive),
    persists outcome and decision margins in database, and appends audit log.
    """
    from app.services.classification_service import ClassificationService
    from app.scientific.classifier import ClassificationPreconditionError

    service = ClassificationService(db)
    try:
        return service.classify_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ClassificationPreconditionError, InvalidTransitionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/seal", response_model=EvidenceSealResponse, status_code=status.HTTP_200_OK)
async def seal_session_evidence(
    session_id: str,
    db: Session = Depends(get_db),
) -> EvidenceSealResponse:
    """
    Cryptographically seals session evidence into an immutable canonical envelope,
    computes SHA-256 digest, and signs with enrolled device Ed25519 key.
    Transitions session to EVIDENCE_SEALED.
    """
    from app.services.evidence_service import EvidenceService

    service = EvidenceService(db)
    try:
        return service.seal_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{session_id}/procedural", response_model=ProceduralContextResponse, status_code=status.HTTP_200_OK)
async def get_session_procedural_context(
    session_id: str,
    db: Session = Depends(get_db),
) -> ProceduralContextResponse:
    """
    Retrieves the authoritative procedural context and statutory safeguard snapshot for a session.
    """
    from app.services.procedural_service import ProceduralService

    service = ProceduralService(db)
    try:
        return service.get_procedural_context(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{session_id}/procedural", response_model=ProceduralContextResponse, status_code=status.HTTP_200_OK)
async def update_session_procedural_context(
    session_id: str,
    data: ProceduralUpdateRequest,
    actor_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> ProceduralContextResponse:
    """
    Updates officer-supplied procedural context metadata (witnesses, memo ref, Section 50/52A/57, kit lot).
    Enforces post-seal immutability: returns HTTP 409 Conflict if session is in EVIDENCE_SEALED state.
    """
    from app.services.procedural_service import ProceduralService, ProceduralImmutabilityError

    service = ProceduralService(db)
    try:
        return service.update_procedural_context(session_id, data, actor_id=actor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProceduralImmutabilityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{session_id}/referral-summary", response_model=ReferralSummaryResponse, status_code=status.HTTP_200_OK)
async def get_session_referral_summary(
    session_id: str,
    db: Session = Depends(get_db),
) -> ReferralSummaryResponse:
    """
    Retrieves aggregated presumptive triage summary metadata for laboratory referral handoff.
    """
    from app.services.procedural_service import ProceduralService

    service = ProceduralService(db)
    try:
        return service.get_referral_summary(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{session_id}/referral/export", status_code=status.HTTP_200_OK)
async def export_formal_referral_package(
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Generates and exports the formal canonical JSON and printable HTML referral package.
    Only allowed for sealed evidence sessions.
    """
    from app.services.referral_service import ReferralService

    service = ReferralService(db)
    try:
        return service.generate_referral_package(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/custody", response_model=CustodyEventResponse, status_code=status.HTTP_201_CREATED)
async def record_custody_handoff_event(
    session_id: str,
    req: CustodyCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Records an officer-entered physical custody handoff event for sealed evidence.
    """
    from app.services.custody_service import CustodyService

    service = CustodyService(db)
    try:
        return service.record_custody_handoff(session_id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{session_id}/custody", response_model=List[CustodyEventResponse], status_code=status.HTTP_200_OK)
async def get_session_custody_history(
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves the complete chronological chain of custody transfer events for a test session.
    """
    from app.services.custody_service import CustodyService

    service = CustodyService(db)
    try:
        return service.get_custody_history(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



