"""REACTRA V2 — Measurement Request & Response Schemas (Pydantic V2)."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class MeasurementExecuteRequest(BaseModel):
    """Request payload for executing image analysis on a session."""
    image_base64: str = Field(..., description="Base64 encoded image data URL or raw string")
    provenance: str = Field(default="LIVE_CAMERA", description="'LIVE_CAMERA' or 'IMPORTED_IMAGE'")
    elapsed_seconds: Optional[float] = Field(default=None, description="Elapsed reaction incubation seconds")


class BlurCheckResponse(BaseModel):
    variance: float
    threshold: float
    passed: bool
    explanation: str
    model_config = ConfigDict(from_attributes=True)


class ExposureCheckResponse(BaseModel):
    mean_luminance: float
    underexposed_fraction: float
    overexposed_fraction: float
    dynamic_range: int
    passed: bool
    explanation: str
    model_config = ConfigDict(from_attributes=True)


class GlareCheckResponse(BaseModel):
    max_roi_glare_fraction: float
    threshold: float
    passed: bool
    explanation: str
    roi_glare_fractions: Dict[str, float]
    model_config = ConfigDict(from_attributes=True)


class CardCheckResponse(BaseModel):
    detected: bool
    confidence: float
    aspect_ratio: float
    area_fraction: float
    reason: str
    model_config = ConfigDict(from_attributes=True)


class CalibrationCheckResponse(BaseModel):
    passed: bool
    mean_delta_e: float
    threshold: float
    explanation: str
    patch_count: int
    patch_diagnostics: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)


class TimingCheckResponse(BaseModel):
    compliance_status: str
    elapsed_seconds: Optional[float]
    target_window_seconds: int
    min_window_seconds: int
    max_window_seconds: int
    passed: bool
    explanation: str
    model_config = ConfigDict(from_attributes=True)


class AlignmentCheckResponse(BaseModel):
    passed: bool
    skew_angle_deg: float
    model_config = ConfigDict(from_attributes=True)


class QualityChecksGroup(BaseModel):
    blur: BlurCheckResponse
    exposure: ExposureCheckResponse
    glare: GlareCheckResponse
    card_detection: CardCheckResponse
    alignment: AlignmentCheckResponse
    calibration: CalibrationCheckResponse
    timing: TimingCheckResponse
    model_config = ConfigDict(from_attributes=True)


class QualityDiagnosticsResponse(BaseModel):
    overall_status: str
    passed_all_hard_gates: bool
    failure_reasons: List[str]
    checks: QualityChecksGroup
    model_config = ConfigDict(from_attributes=True)


class WellColorMeasurementResponse(BaseModel):
    roi_id: str
    name: str
    bbox: List[int]
    sampled_bbox: List[int]
    valid_pixel_count: int
    glare_pixel_count: int
    raw_lab_median: List[float]
    calibrated_lab_median: List[float]
    calibrated_lab_trimmed_mean: List[float]
    lab_std_dev: List[float]
    is_valid: bool
    rejection_reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ValidatedMeasurementResponse(BaseModel):
    measurement_id: str
    session_id: str
    capture_id: str
    profile_id: str
    profile_version: str
    algorithm_version: str
    reference_card_version: str
    provenance: str
    measured_at: str
    timing_compliance: str
    elapsed_seconds: Optional[float]
    calibration_mean_delta_e: float
    calibration_passed: bool
    well_measurements: Dict[str, WellColorMeasurementResponse]
    quality_diagnostics: QualityDiagnosticsResponse
    model_config = ConfigDict(from_attributes=True)


class MeasurementExecutionOutcomeResponse(BaseModel):
    """Consolidated outcome of the measurement execution API."""
    session_id: str
    session_status: str
    passed_quality_gates: bool
    overall_quality_status: str
    quality_diagnostics: QualityDiagnosticsResponse
    validated_measurement: Optional[ValidatedMeasurementResponse] = None
    model_config = ConfigDict(from_attributes=True)
