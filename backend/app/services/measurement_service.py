"""REACTRA V2 — Authoritative Measurement Service.

Orchestrates image capture validation, scientific pipeline execution,
quality gate enforcement, database persistence, and audit logging.
Section References: PRD V2 §10-14, Master Build Spec §10-14.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

logger = logging.getLogger("reactra.measurement_service")

from app.db.models.audit import AuditEvent
from app.domain.identifiers import generate_capture_id, generate_event_id
from app.domain.state_machine import SessionState, SessionStateMachine, InvalidTransitionError
from app.repositories.session_repository import SessionRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.scientific.profiles import get_scientific_profile
from app.scientific.measurement import (
    execute_scientific_measurement,
    ValidatedMeasurement,
    MeasurementQualityError,
)
from app.scientific.image_io import ImageValidationError
from app.schemas.measurement import (
    MeasurementExecutionOutcomeResponse,
    ValidatedMeasurementResponse,
    QualityDiagnosticsResponse,
    QualityChecksGroup,
    BlurCheckResponse,
    ExposureCheckResponse,
    GlareCheckResponse,
    CardCheckResponse,
    AlignmentCheckResponse,
    CalibrationCheckResponse,
    TimingCheckResponse,
    WellColorMeasurementResponse,
)


def _diagnostics_to_schema(diag) -> QualityDiagnosticsResponse:
    """Convert scientific QualityDiagnostics object to Pydantic schema."""
    d = diag.to_dict()
    c = d["checks"]
    return QualityDiagnosticsResponse(
        overall_status=d["overall_status"],
        passed_all_hard_gates=d["passed_all_hard_gates"],
        failure_reasons=d["failure_reasons"],
        checks=QualityChecksGroup(
            blur=BlurCheckResponse(**c["blur"]),
            exposure=ExposureCheckResponse(**c["exposure"]),
            glare=GlareCheckResponse(**c["glare"]),
            card_detection=CardCheckResponse(**c["card_detection"]),
            alignment=AlignmentCheckResponse(**c["alignment"]),
            calibration=CalibrationCheckResponse(**c["calibration"]),
            timing=TimingCheckResponse(**c["timing"]),
        ),
    )


def _validated_measurement_to_schema(meas: ValidatedMeasurement) -> ValidatedMeasurementResponse:
    """Convert scientific ValidatedMeasurement domain object to Pydantic schema."""
    d = meas.to_dict()
    well_responses = {}
    for wid, wdict in d["well_measurements"].items():
        well_responses[wid] = WellColorMeasurementResponse(**wdict)

    return ValidatedMeasurementResponse(
        measurement_id=d["measurement_id"],
        session_id=d["session_id"],
        capture_id=d["capture_id"],
        profile_id=d["profile_id"],
        profile_version=d["profile_version"],
        algorithm_version=d["algorithm_version"],
        reference_card_version=d["reference_card_version"],
        provenance=d["provenance"],
        measured_at=d["measured_at"],
        timing_compliance=d["timing_compliance"],
        elapsed_seconds=d["elapsed_seconds"],
        calibration_mean_delta_e=d["calibration_mean_delta_e"],
        calibration_passed=d["calibration_passed"],
        well_measurements=well_responses,
        quality_diagnostics=_diagnostics_to_schema(meas.quality_diagnostics),
    )


class MeasurementService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditRepository(db)
        self.measurement_repo = MeasurementRepository(db)

    def process_capture_and_measure(
        self,
        session_id: str,
        image_source: str,  # Base64 data URL or filepath
        provenance: str = "LIVE_CAMERA",
        elapsed_seconds: Optional[float] = None,
        operator_id: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> MeasurementExecutionOutcomeResponse:
        """Process an image capture through the scientific pipeline with quality gating.
        
        Enforces:
        - If quality passes: session transitions to READY_FOR_CLASSIFICATION, measurement is stored,
          and a ValidatedMeasurement is returned.
        - If quality fails: session transitions to VALIDATION_FAILED, failure diagnostics are stored,
          and NO ValidatedMeasurement is produced.
        """
        session = self.session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session '{session_id}' not found.")

        # Step into CAPTURED -> QUALITY_CHECKING via state machine
        if session.status in (SessionState.DRAFT.value, SessionState.VALIDATION_FAILED.value, SessionState.READY_FOR_CLASSIFICATION.value):
            SessionStateMachine.validate_transition(session.status, SessionState.CAPTURED)
            self.session_repo.update_status(session, SessionState.CAPTURED.value)
        
        if session.status == SessionState.CAPTURED.value:
            SessionStateMachine.validate_transition(session.status, SessionState.QUALITY_CHECKING)
            self.session_repo.update_status(session, SessionState.QUALITY_CHECKING.value)

        # Load scientific profile
        profile = get_scientific_profile(session.assay_profile_id)
        capture_id = generate_capture_id()
        actor = operator_id or session.operator_id
        dev_id = device_id or session.device_enrollment_id
        now_utc = datetime.now(timezone.utc)

        logger.info(
            f"[MEASURE DISPATCH] Session={session_id} | State={session.status} | "
            f"CaptureID={capture_id} | Provenance={provenance} | Profile={profile.profile_id} ({profile.profile_version})"
        )

        # Record capture start in audit log
        self.audit_repo.append(
            AuditEvent(
                event_id=generate_event_id(),
                test_id=session_id,
                event_type="CAPTURE_INITIATED",
                from_state=session.status,
                to_state=SessionState.QUALITY_CHECKING.value,
                actor_id=actor,
                device_enrollment_id=dev_id,
                event_payload={"capture_id": capture_id, "provenance": provenance},
                event_timestamp_utc=now_utc,
            )
        )

        try:
            # Execute the pure scientific pipeline
            validated_meas = execute_scientific_measurement(
                image_source=image_source,
                session_id=session_id,
                capture_id=capture_id,
                provenance=provenance,
                profile=profile,
                elapsed_seconds=elapsed_seconds,
            )

            # Register in classification store
            from app.services.classification_service import register_validated_measurement
            register_validated_measurement(session_id, validated_meas)

            # Success path: Transition session status to READY_FOR_CLASSIFICATION
            SessionStateMachine.validate_transition(session.status, SessionState.READY_FOR_CLASSIFICATION, quality_passed=True)
            self.session_repo.update_status(session, SessionState.READY_FOR_CLASSIFICATION.value)

            # Persist CaptureRecord
            self.measurement_repo.create_capture_record(
                capture_id=capture_id,
                session_id=session_id,
                provenance=provenance,
                image_path=f"memory://capture/{capture_id}.png",
                image_sha256=capture_id,
                quality_status="READY",
                width=profile.canonical_card_width,
                height=profile.canonical_card_height,
            )

            # Extract primary reaction well values
            primary_well = validated_meas.well_measurements.get("well_1")
            lab_l = primary_well.calibrated_lab_median[0] if primary_well else None
            lab_a = primary_well.calibrated_lab_median[1] if primary_well else None
            lab_b = primary_well.calibrated_lab_median[2] if primary_well else None
            valid_px = primary_well.valid_pixel_count if primary_well else None
            glare_px = primary_well.glare_pixel_count if primary_well else None

            # Persist MeasurementResult
            self.measurement_repo.save_or_update_measurement(
                session_id=session_id,
                quality_status="READY",
                card_detection_confidence=validated_meas.quality_diagnostics.card_detection.confidence,
                calibration_residual=validated_meas.calibration_mean_delta_e,
                blur_metric=validated_meas.quality_diagnostics.blur.variance,
                exposure_metric=validated_meas.quality_diagnostics.exposure.mean_luminance,
                glare_metric=validated_meas.quality_diagnostics.glare.max_roi_glare_fraction,
                reaction_lab_l=lab_l,
                reaction_lab_a=lab_a,
                reaction_lab_b=lab_b,
                roi_pixel_count=valid_px,
                specular_rejected_pixel_count=glare_px,
                specular_rejected_fraction=float(glare_px / (valid_px + glare_px)) if (valid_px and glare_px) else 0.0,
                algorithm_version=profile.algorithm_version,
                model_version=profile.profile_version,
            )

            # Audit event for valid measurement
            self.audit_repo.append(
                AuditEvent(
                    event_id=generate_event_id(),
                    test_id=session_id,
                    event_type="MEASUREMENT_VALIDATED",
                    from_state=SessionState.QUALITY_CHECKING.value,
                    to_state=SessionState.READY_FOR_CLASSIFICATION.value,
                    actor_id=actor,
                    device_enrollment_id=dev_id,
                    event_payload={
                        "measurement_id": validated_meas.measurement_id,
                        "calibration_residual": validated_meas.calibration_mean_delta_e,
                        "primary_well_lab": [lab_l, lab_a, lab_b],
                    },
                    event_timestamp_utc=datetime.now(timezone.utc),
                )
            )

            self.db.commit()

            return MeasurementExecutionOutcomeResponse(
                session_id=session_id,
                session_status=SessionState.READY_FOR_CLASSIFICATION.value,
                passed_quality_gates=True,
                overall_quality_status="READY",
                quality_diagnostics=_diagnostics_to_schema(validated_meas.quality_diagnostics),
                validated_measurement=_validated_measurement_to_schema(validated_meas),
            )

        except MeasurementQualityError as q_err:
            # Quality Gate Rejection Path: Transition to VALIDATION_FAILED
            self.session_repo.update_status(session, SessionState.VALIDATION_FAILED.value)

            # Persist CaptureRecord with failure status
            self.measurement_repo.create_capture_record(
                capture_id=capture_id,
                session_id=session_id,
                provenance=provenance,
                image_path=f"memory://capture/{capture_id}.png",
                image_sha256=capture_id,
                quality_status=q_err.diagnostics.overall_status,
                width=profile.canonical_card_width,
                height=profile.canonical_card_height,
            )

            # Persist MeasurementResult with failure status
            self.measurement_repo.save_or_update_measurement(
                session_id=session_id,
                quality_status=q_err.diagnostics.overall_status,
                card_detection_confidence=q_err.diagnostics.card_detection.confidence,
                calibration_residual=q_err.diagnostics.calibration.mean_delta_e,
                blur_metric=q_err.diagnostics.blur.variance,
                exposure_metric=q_err.diagnostics.exposure.mean_luminance,
                glare_metric=q_err.diagnostics.glare.max_roi_glare_fraction,
                algorithm_version=profile.algorithm_version,
                model_version=profile.profile_version,
            )

            # Audit event for rejection
            self.audit_repo.append(
                AuditEvent(
                    event_id=generate_event_id(),
                    test_id=session_id,
                    event_type="MEASUREMENT_VALIDATION_FAILED",
                    from_state=SessionState.QUALITY_CHECKING.value,
                    to_state=SessionState.VALIDATION_FAILED.value,
                    actor_id=actor,
                    device_enrollment_id=dev_id,
                    event_payload={
                        "failure_reasons": q_err.diagnostics.failure_reasons,
                        "overall_status": q_err.diagnostics.overall_status,
                    },
                    event_timestamp_utc=datetime.now(timezone.utc),
                )
            )

            self.db.commit()

            return MeasurementExecutionOutcomeResponse(
                session_id=session_id,
                session_status=SessionState.VALIDATION_FAILED.value,
                passed_quality_gates=False,
                overall_quality_status=q_err.diagnostics.overall_status,
                quality_diagnostics=_diagnostics_to_schema(q_err.diagnostics),
                validated_measurement=None,
            )
