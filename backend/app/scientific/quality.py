"""REACTRA V2 — Adaptive Capture Guard Quality Aggregator.

Aggregates optical, geometric, and calibration checks into a structured diagnostic report.
Section References: PRD V2 §10, Master Build Spec §10.
"""

from typing import Dict, List, Optional, Any

from app.scientific.blur import BlurMetricResult
from app.scientific.exposure import ExposureMetricResult
from app.scientific.glare import GlareMetricResult
from app.scientific.card_detection import CardDetectionResult
from app.scientific.calibration import CalibrationResult
from app.scientific.timing_gate import TimingGateResult


class QualityDiagnostics:
    """Consolidated diagnostic report of all Adaptive Capture Guard checks."""
    def __init__(
        self,
        overall_status: str,  # 'READY', 'REVIEW', 'RECAPTURE', 'INVALID'
        passed_all_hard_gates: bool,
        blur: BlurMetricResult,
        exposure: ExposureMetricResult,
        glare: GlareMetricResult,
        card_detection: CardDetectionResult,
        alignment_passed: bool,
        skew_angle_deg: float,
        calibration: CalibrationResult,
        timing: TimingGateResult,
        failure_reasons: List[str],
    ):
        self.overall_status = overall_status
        self.passed_all_hard_gates = passed_all_hard_gates
        self.blur = blur
        self.exposure = exposure
        self.glare = glare
        self.card_detection = card_detection
        self.alignment_passed = alignment_passed
        self.skew_angle_deg = skew_angle_deg
        self.calibration = calibration
        self.timing = timing
        self.failure_reasons = failure_reasons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "passed_all_hard_gates": self.passed_all_hard_gates,
            "failure_reasons": self.failure_reasons,
            "checks": {
                "blur": self.blur.to_dict(),
                "exposure": self.exposure.to_dict(),
                "glare": self.glare.to_dict(),
                "card_detection": {
                    "detected": self.card_detection.detected,
                    "confidence": round(self.card_detection.confidence, 3),
                    "aspect_ratio": round(self.card_detection.aspect_ratio, 3),
                    "area_fraction": round(self.card_detection.area_fraction, 3),
                    "reason": self.card_detection.reason,
                },
                "alignment": {
                    "passed": self.alignment_passed,
                    "skew_angle_deg": round(self.skew_angle_deg, 1),
                },
                "calibration": self.calibration.to_dict(),
                "timing": self.timing.to_dict(),
            },
        }


def aggregate_quality_diagnostics(
    blur: BlurMetricResult,
    exposure: ExposureMetricResult,
    glare: GlareMetricResult,
    card_detection: CardDetectionResult,
    calibration: CalibrationResult,
    timing: TimingGateResult,
    max_skew_angle_deg: float = 20.0,
) -> QualityDiagnostics:
    """Aggregate individual quality checks into an authoritative quality verdict."""
    failure_reasons: List[str] = []

    # 1. Card Detection Gate
    if not card_detection.detected:
        failure_reasons.append("Reference card could not be localized in capture.")

    # 2. Alignment Gate
    alignment_passed = card_detection.skew_angle_deg <= max_skew_angle_deg
    if not alignment_passed:
        failure_reasons.append(
            f"Perspective skew excessive ({card_detection.skew_angle_deg:.1f}° > {max_skew_angle_deg:.1f}°)."
        )

    # 3. Blur Gate
    if not blur.passed:
        failure_reasons.append(f"Image blur excessive: {blur.explanation}")

    # 4. Exposure Gate
    if not exposure.passed:
        failure_reasons.append(f"Illumination invalid: {exposure.explanation}")

    # 5. Glare Gate
    if not glare.passed:
        failure_reasons.append(f"Specular glare in reaction zone: {glare.explanation}")

    # 6. Calibration Gate
    if not calibration.passed:
        failure_reasons.append(f"Color calibration failed: {calibration.explanation}")

    # 7. Timing Gate
    if not timing.passed:
        failure_reasons.append(f"Reaction timing invalid: {timing.explanation}")

    # Determine overall status
    if len(failure_reasons) == 0:
        overall_status = "READY"
        passed_all_hard_gates = True
    elif not card_detection.detected or not timing.passed:
        overall_status = "INVALID"
        passed_all_hard_gates = False
    elif not blur.passed or not glare.passed or not exposure.passed or not calibration.passed:
        overall_status = "RECAPTURE"
        passed_all_hard_gates = False
    else:
        overall_status = "REVIEW"
        passed_all_hard_gates = False

    return QualityDiagnostics(
        overall_status=overall_status,
        passed_all_hard_gates=passed_all_hard_gates,
        blur=blur,
        exposure=exposure,
        glare=glare,
        card_detection=card_detection,
        alignment_passed=alignment_passed,
        skew_angle_deg=card_detection.skew_angle_deg,
        calibration=calibration,
        timing=timing,
        failure_reasons=failure_reasons,
    )
