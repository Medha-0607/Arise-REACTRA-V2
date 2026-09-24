"""
Pydantic Schemas for Test Sessions, Transitions, and Audit Events (Pydantic V2).
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.domain.state_machine import SessionState, CaptureSource, GpsStatus


class SessionCreateRequest(BaseModel):
    case_id: str = Field(..., description="Case or incident identifier")
    event_id: Optional[str] = Field(None, description="Optional incident event number")
    operator_id: str = Field(..., description="Badge or operator ID")
    field_officer_name: Optional[str] = None
    field_officer_designation: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None
    
    assay_profile_id: str = Field(default="marquis-standard-v1")
    assay_profile_version: str = Field(default="v1.0.0")
    capture_mode: CaptureSource = Field(default=CaptureSource.LIVE_CAMERA)
    
    # Location Provenance (Explicitly never fabricated)
    gps_status: GpsStatus = Field(default=GpsStatus.OPERATOR_DECLARED)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy: Optional[float] = None
    location_description: Optional[str] = None
    
    # Device & Mode Metadata (Explicit demo vs normal field boundary)
    device_enrollment_id: Optional[str] = Field(
        default=None,
        description="Authoritative device enrollment ID (e.g. DEV-UNIT-01). Required for normal production/field sessions."
    )
    is_demo_mode: bool = Field(
        default=False,
        description="Explicit flag declaring whether the session is conducted in demo/un-enrolled simulation mode."
    )

    # Procedural initial context
    search_context_type: Optional[str] = None
    panchnama_memo_ref_no: Optional[str] = None
    officer_notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_device_identity(self) -> "SessionCreateRequest":
        if not self.is_demo_mode:
            if not self.device_enrollment_id or not self.device_enrollment_id.strip():
                raise ValueError(
                    "Missing authoritative device_enrollment_id. Normal field/production sessions require an explicit "
                    "device enrollment ID. For un-enrolled demo/simulation, explicitly set is_demo_mode=True."
                )
        return self


class SessionTransitionRequest(BaseModel):
    target_state: SessionState = Field(..., description="Target domain state to transition into")
    actor_id: Optional[str] = Field(None, description="Operator or subsystem requesting transition")
    quality_passed: Optional[bool] = Field(None, description="Result of optical quality gate evaluation")
    event_payload: Optional[Dict[str, Any]] = Field(None, description="Metadata associated with transition event")


class AuditEventResponse(BaseModel):
    event_id: str
    test_id: str
    event_type: str
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    actor_id: str
    device_enrollment_id: str
    event_payload: Optional[Dict[str, Any]] = None
    event_timestamp_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class ReactionTimingResponse(BaseModel):
    reaction_started_at_utc: Optional[datetime] = None
    capture_timestamp_utc: Optional[datetime] = None
    capture_elapsed_seconds: Optional[float] = None
    timer_source: str
    kinetic_window_status: str
    t_min_seconds_snapshot: float
    t_max_seconds_snapshot: float

    model_config = ConfigDict(from_attributes=True)


class MeasurementResultResponse(BaseModel):
    quality_status: str
    result: Optional[str] = None
    card_detection_confidence: Optional[float] = None
    blur_metric: Optional[float] = None
    exposure_metric: Optional[float] = None
    glare_metric: Optional[float] = None
    reaction_lab_l: Optional[float] = None
    reaction_lab_a: Optional[float] = None
    reaction_lab_b: Optional[float] = None
    algorithm_version: str
    model_version: str

    model_config = ConfigDict(from_attributes=True)


class EvidenceRecordResponse(BaseModel):
    id: str
    image_reference: Optional[str] = None
    image_sha256: Optional[str] = None
    record_digest: Optional[str] = None
    signature: Optional[str] = None
    integrity_status: str
    sealed_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class ProceduralContextResponse(BaseModel):
    search_context_type: Optional[str] = None
    authorization_reference: Optional[str] = None
    panchnama_memo_ref_no: Optional[str] = None
    panch_witness_1_name: Optional[str] = None
    panch_witness_2_name: Optional[str] = None
    officer_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SessionSummaryResponse(BaseModel):
    id: str
    case_id: str
    event_id: Optional[str] = None
    operator_id: str
    assay_profile_id: str
    assay_profile_version: str
    status: str
    capture_mode: str
    gps_status: str
    location_description: Optional[str] = None
    created_at_utc: datetime
    updated_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionDetailResponse(SessionSummaryResponse):
    field_officer_name: Optional[str] = None
    field_officer_designation: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None
    sync_state: str
    device_enrollment_id: str
    
    timing: Optional[ReactionTimingResponse] = None
    measurement: Optional[MeasurementResultResponse] = None
    procedural_context: Optional[ProceduralContextResponse] = None
    evidence: Optional[EvidenceRecordResponse] = None
    audit_events: List[AuditEventResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SessionTimelineResponse(BaseModel):
    session_id: str
    current_status: str
    events: List[AuditEventResponse]
