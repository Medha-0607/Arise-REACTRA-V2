"""REACTRA V2 — Measurement & Capture Repositories.

Encapsulates database persistence for CaptureRecord and MeasurementResult entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.capture import CaptureRecord
from app.db.models.measurement import MeasurementResult


class MeasurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_session_id(self, session_id: str) -> Optional[MeasurementResult]:
        """Retrieve MeasurementResult associated with a session."""
        stmt = select(MeasurementResult).where(MeasurementResult.test_id == session_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_measurement(self, session_id: str) -> Optional[MeasurementResult]:
        """Alias for get_by_session_id."""
        return self.get_by_session_id(session_id)

    def save_or_update_measurement(
        self,
        session_id: str,
        quality_status: str,
        card_detection_confidence: Optional[float] = None,
        calibration_residual: Optional[float] = None,
        blur_metric: Optional[float] = None,
        exposure_metric: Optional[float] = None,
        glare_metric: Optional[float] = None,
        reaction_lab_l: Optional[float] = None,
        reaction_lab_a: Optional[float] = None,
        reaction_lab_b: Optional[float] = None,
        roi_pixel_count: Optional[int] = None,
        specular_rejected_pixel_count: Optional[int] = None,
        specular_rejected_fraction: Optional[float] = None,
        algorithm_version: str = "2.0.0",
        model_version: str = "1.0.0",
    ) -> MeasurementResult:
        """Create or update the authoritative MeasurementResult record."""
        existing = self.get_by_session_id(session_id)
        if existing is None:
            existing = MeasurementResult(
                test_id=session_id,
                quality_status=quality_status,
                algorithm_version=algorithm_version,
                model_version=model_version,
            )
            self.db.add(existing)

        existing.quality_status = quality_status
        existing.card_detection_confidence = card_detection_confidence
        existing.calibration_residual = calibration_residual
        existing.blur_metric = blur_metric
        existing.exposure_metric = exposure_metric
        existing.glare_metric = glare_metric
        existing.reaction_lab_l = reaction_lab_l
        existing.reaction_lab_a = reaction_lab_a
        existing.reaction_lab_b = reaction_lab_b
        existing.roi_pixel_count = roi_pixel_count
        existing.specular_rejected_pixel_count = specular_rejected_pixel_count
        existing.specular_rejected_fraction = specular_rejected_fraction
        existing.algorithm_version = algorithm_version
        existing.model_version = model_version

        self.db.flush()
        return existing

    def create_capture_record(
        self,
        capture_id: str,
        session_id: str,
        provenance: str,
        image_path: str,
        image_sha256: str,
        quality_status: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> CaptureRecord:
        """Create a new CaptureRecord."""
        record = CaptureRecord(
            id=capture_id,
            session_id=session_id,
            provenance=provenance,
            image_path=image_path,
            image_sha256=image_sha256,
            quality_status=quality_status,
            width=width,
            height=height,
        )
        self.db.add(record)
        self.db.flush()
        return record
