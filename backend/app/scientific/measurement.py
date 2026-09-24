"""REACTRA V2 — Scientific Measurement Pipeline & ValidatedMeasurement Contract.

Executes the complete scientific image analysis pipeline:
Image Ingestion -> Provenance Validation -> Card Detection -> Perspective Warp ->
Quality Analysis -> Color Calibration -> ROI Extraction -> Glare Filtering ->
Robust Color Estimation -> ValidatedMeasurement Domain Contract.

CRITICAL NON-NEGOTIABLE RULE:
The classifier receives ONLY a ValidatedMeasurement domain object, NEVER the raw image.
If any mandatory quality or calibration gate fails, NO ValidatedMeasurement is produced.
Section References: PRD V2 §10-14, Master Build Spec §10-14.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np

logger = logging.getLogger("reactra.measurement")

from app.domain.identifiers import generate_measurement_id
from app.scientific.image_io import ingest_image_data, IngestedImage, ImageValidationError
from app.scientific.card_detection import detect_reference_card, CardDetectionResult
from app.scientific.perspective import normalize_card_perspective, PerspectiveResult
from app.scientific.blur import evaluate_blur, BlurMetricResult
from app.scientific.exposure import evaluate_exposure, ExposureMetricResult
from app.scientific.glare import detect_specular_glare, GlareMetricResult
from app.scientific.calibration import calibrate_reference_card, CalibrationResult
from app.scientific.roi import extract_reaction_rois, ExtractedRoi
from app.scientific.robust_estimation import robust_estimate_well_color, WellColorMeasurement
from app.scientific.timing_gate import evaluate_reaction_timing, TimingGateResult
from app.scientific.quality import aggregate_quality_diagnostics, QualityDiagnostics
from app.scientific.profiles import ScientificAssayProfile, get_scientific_profile


class MeasurementQualityError(Exception):
    """Raised when an image capture fails quality gating or calibration."""
    def __init__(self, message: str, diagnostics: QualityDiagnostics, capture_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.diagnostics = diagnostics
        self.capture_id = capture_id


class ValidatedMeasurement:
    """Authoritative scientific measurement domain contract.
    
    Contains all calibrated colorimetric and diagnostic data required for
    future classification without needing the raw image.
    """
    def __init__(
        self,
        measurement_id: str,
        session_id: str,
        capture_id: str,
        profile_id: str,
        profile_version: str,
        algorithm_version: str,
        reference_card_version: str,
        provenance: str,
        measured_at: str,
        timing_compliance: str,
        elapsed_seconds: Optional[float],
        calibration_mean_delta_e: float,
        calibration_passed: bool,
        well_measurements: Dict[str, WellColorMeasurement],
        quality_diagnostics: QualityDiagnostics,
    ):
        self.measurement_id = measurement_id
        self.session_id = session_id
        self.capture_id = capture_id
        self.profile_id = profile_id
        self.profile_version = profile_version
        self.algorithm_version = algorithm_version
        self.reference_card_version = reference_card_version
        self.provenance = provenance
        self.measured_at = measured_at
        self.timing_compliance = timing_compliance
        self.elapsed_seconds = elapsed_seconds
        self.calibration_mean_delta_e = calibration_mean_delta_e
        self.calibration_passed = calibration_passed
        self.well_measurements = well_measurements
        self.quality_diagnostics = quality_diagnostics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "session_id": self.session_id,
            "capture_id": self.capture_id,
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "algorithm_version": self.algorithm_version,
            "reference_card_version": self.reference_card_version,
            "provenance": self.provenance,
            "measured_at": self.measured_at,
            "timing_compliance": self.timing_compliance,
            "elapsed_seconds": self.elapsed_seconds,
            "calibration_mean_delta_e": round(self.calibration_mean_delta_e, 2),
            "calibration_passed": self.calibration_passed,
            "well_measurements": {k: v.to_dict() for k, v in self.well_measurements.items()},
            "quality_diagnostics": self.quality_diagnostics.to_dict(),
        }


def execute_scientific_measurement(
    image_source: Union[bytes, str],
    session_id: str,
    capture_id: str,
    provenance: str = "LIVE_CAMERA",
    profile: Optional[ScientificAssayProfile] = None,
    elapsed_seconds: Optional[float] = None,
) -> ValidatedMeasurement:
    """Execute the full Adaptive Capture Guard and scientific measurement pipeline."""
    if profile is None:
        profile = get_scientific_profile("marquis-standard-v1")

    # Stage 1: Ingest & Validate Raw Image Input
    ingested = ingest_image_data(image_source=image_source, provenance=provenance)
    received_aspect_ratio = float(ingested.width) / float(ingested.height) if ingested.height > 0 else 0.0

    logger.info(
        f"[MEASUREMENT BOUNDARY] Session={session_id} | Provenance={provenance} | "
        f"Format={ingested.source_format} | Dimensions={ingested.width}x{ingested.height} | "
        f"AspectRatio={received_aspect_ratio:.3f} | SHA-256={ingested.sha256_hash[:16]}..."
    )

    # Stage 2: Reference Card Detection
    card_res = detect_reference_card(
        rgb_image=ingested.rgb_array,
        target_aspect_ratio=profile.card_aspect_ratio,
    )

    logger.info(
        f"[CARD LOCALIZATION] Session={session_id} | Detected={card_res.detected} | "
        f"Confidence={card_res.confidence * 100:.1f}% | DetectedRatio={card_res.aspect_ratio:.3f} | "
        f"Skew={card_res.skew_angle_deg:.1f}° | Reason='{card_res.reason}'"
    )

    if not card_res.detected or card_res.corners is None:
        # Card detection failure: construct diagnostics and reject
        dummy_blur = evaluate_blur(ingested.rgb_array, profile.thresholds.min_laplacian_variance)
        dummy_exposure = evaluate_exposure(ingested.rgb_array)
        dummy_glare = GlareMetricResult(
            glare_mask=np.zeros((10, 10), dtype=np.uint8),
            max_roi_glare_fraction=0.0,
            threshold=profile.thresholds.max_glare_roi_fraction,
            passed=True,
            explanation="Not evaluated (card missing)",
            roi_glare_fractions={},
        )
        dummy_calib = CalibrationResult(
            passed=False,
            mean_delta_e=999.0,
            threshold=profile.thresholds.max_calibration_delta_e,
            affine_matrix=np.eye(3, 4),
            patch_diagnostics={},
            explanation="Not evaluated (card missing)",
        )
        timing_res = evaluate_reaction_timing(
            elapsed_seconds=elapsed_seconds,
            target_window_seconds=profile.target_reaction_window_seconds,
            min_window_seconds=profile.min_reaction_window_seconds,
            max_window_seconds=profile.max_reaction_window_seconds,
        )
        diag = aggregate_quality_diagnostics(
            blur=dummy_blur,
            exposure=dummy_exposure,
            glare=dummy_glare,
            card_detection=card_res,
            calibration=dummy_calib,
            timing=timing_res,
            max_skew_angle_deg=profile.thresholds.max_skew_angle_deg,
        )
        raise MeasurementQualityError(
            message="Reference card could not be detected in capture.",
            diagnostics=diag,
            capture_id=capture_id,
        )

    # Stage 3: Perspective Normalization
    warp_res = normalize_card_perspective(
        rgb_image=ingested.rgb_array,
        ordered_corners=card_res.corners,
        canonical_width=profile.canonical_card_width,
        canonical_height=profile.canonical_card_height,
    )
    canonical_rgb = warp_res.warped_rgb

    # Stage 4: Optical Quality Analysis on Canonical Card
    blur_res = evaluate_blur(canonical_rgb, profile.thresholds.min_laplacian_variance)
    exposure_res = evaluate_exposure(
        canonical_rgb,
        min_mean_luminance=profile.thresholds.min_mean_luminance,
        max_mean_luminance=profile.thresholds.max_mean_luminance,
        max_underexposure_fraction=profile.thresholds.max_underexposure_fraction,
        max_overexposure_fraction=profile.thresholds.max_overexposure_fraction,
    )

    # Collect ROI coordinates for glare detection
    roi_tuples = [(r.roi_id, r.bbox) for r in profile.reaction_rois]
    glare_res = detect_specular_glare(
        canonical_rgb,
        reaction_rois=roi_tuples,
        max_glare_fraction=profile.thresholds.max_glare_roi_fraction,
    )

    # Stage 5: Reference Card Color Calibration
    calib_res = calibrate_reference_card(
        canonical_card_rgb=canonical_rgb,
        patch_definitions=profile.calibration_patches,
        max_delta_e_threshold=profile.thresholds.max_calibration_delta_e,
    )

    # Stage 6: Kinetic Reaction Timing Gate
    timing_res = evaluate_reaction_timing(
        elapsed_seconds=elapsed_seconds,
        target_window_seconds=profile.target_reaction_window_seconds,
        min_window_seconds=profile.min_reaction_window_seconds,
        max_window_seconds=profile.max_reaction_window_seconds,
    )

    # Stage 7: Aggregate Quality Diagnostics & Evaluate Hard Gates
    diag = aggregate_quality_diagnostics(
        blur=blur_res,
        exposure=exposure_res,
        glare=glare_res,
        card_detection=card_res,
        calibration=calib_res,
        timing=timing_res,
        max_skew_angle_deg=profile.thresholds.max_skew_angle_deg,
    )

    if not diag.passed_all_hard_gates:
        # Rejection: hard gate failed
        raise MeasurementQualityError(
            message=f"Capture failed quality verification: {'; '.join(diag.failure_reasons)}",
            diagnostics=diag,
            capture_id=capture_id,
        )

    # Stage 8: Extract ROIs & Robust Color Estimation
    extracted_rois = extract_reaction_rois(canonical_rgb, profile.reaction_rois)
    well_measurements: Dict[str, WellColorMeasurement] = {}

    for roi in extracted_rois:
        well_meas = robust_estimate_well_color(
            extracted_roi=roi,
            glare_mask=glare_res.glare_mask,
            calibration=calib_res,
            min_valid_pixels=50,
        )
        if not well_meas.is_valid:
            # Rejection due to ROI failure
            diag.passed_all_hard_gates = False
            diag.overall_status = "RECAPTURE"
            diag.failure_reasons.append(f"ROI '{roi.name}' invalid: {well_meas.rejection_reason}")
            raise MeasurementQualityError(
                message=f"Reaction well extraction failed: {well_meas.rejection_reason}",
                diagnostics=diag,
                capture_id=capture_id,
            )
        well_measurements[roi.roi_id] = well_meas

    # Stage 9: Construct and Return ValidatedMeasurement Contract
    measurement_id = generate_measurement_id()
    now_iso = datetime.now(timezone.utc).isoformat()

    return ValidatedMeasurement(
        measurement_id=measurement_id,
        session_id=session_id,
        capture_id=capture_id,
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        algorithm_version=profile.algorithm_version,
        reference_card_version=profile.reference_card_version,
        provenance=ingested.provenance,
        measured_at=now_iso,
        timing_compliance=timing_res.compliance_status,
        elapsed_seconds=timing_res.elapsed_seconds,
        calibration_mean_delta_e=calib_res.mean_delta_e,
        calibration_passed=calib_res.passed,
        well_measurements=well_measurements,
        quality_diagnostics=diag,
    )
