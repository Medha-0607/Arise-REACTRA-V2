"""REACTRA V2 — Exposure & Dynamic Range Quality Analysis.

Evaluates mean luminance, underexposure/overexposure clipping fractions,
and usable dynamic range.
Section References: PRD V2 §10, Master Build Spec §10.
"""

from typing import Dict, Any
import cv2
import numpy as np


class ExposureMetricResult:
    """Diagnostic container for exposure and dynamic range analysis."""
    def __init__(
        self,
        mean_luminance: float,
        underexposed_fraction: float,
        overexposed_fraction: float,
        dynamic_range: int,
        passed: bool,
        explanation: str,
    ):
        self.mean_luminance = mean_luminance
        self.underexposed_fraction = underexposed_fraction
        self.overexposed_fraction = overexposed_fraction
        self.dynamic_range = dynamic_range
        self.passed = passed
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_luminance": round(self.mean_luminance, 1),
            "underexposed_fraction": round(self.underexposed_fraction, 4),
            "overexposed_fraction": round(self.overexposed_fraction, 4),
            "dynamic_range": self.dynamic_range,
            "passed": self.passed,
            "explanation": self.explanation,
        }


def evaluate_exposure(
    rgb_image: np.ndarray,
    min_mean_luminance: float = 40.0,
    max_mean_luminance: float = 220.0,
    max_underexposure_fraction: float = 0.15,
    max_overexposure_fraction: float = 0.10,
) -> ExposureMetricResult:
    """Evaluate image illumination, clipping, and dynamic range.
    
    Parameters
    ----------
    rgb_image : np.ndarray
        RGB image array.
    min_mean_luminance, max_mean_luminance : float
        Acceptable range for global average luminance.
    max_underexposure_fraction : float
        Maximum allowed fraction of dark clipped pixels (< 15).
    max_overexposure_fraction : float
        Maximum allowed fraction of blown-out clipped pixels (> 245).
        
    Returns
    -------
    ExposureMetricResult
    """
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    total_pixels = float(gray.size)

    mean_luma = float(np.mean(gray))
    min_val = int(np.min(gray))
    max_val = int(np.max(gray))
    dynamic_range = max_val - min_val

    # Underexposure clipping: pixels < 15
    under_count = int(np.sum(gray < 15))
    under_frac = under_count / total_pixels

    # Overexposure clipping: pixels > 245
    over_count = int(np.sum(gray > 245))
    over_frac = over_count / total_pixels

    passed = True
    issues = []

    if mean_luma < min_mean_luminance:
        passed = False
        issues.append(f"Image severely underexposed (mean luma: {mean_luma:.1f} < {min_mean_luminance:.1f})")
    elif mean_luma > max_mean_luminance:
        passed = False
        issues.append(f"Image severely overexposed (mean luma: {mean_luma:.1f} > {max_mean_luminance:.1f})")

    if under_frac > max_underexposure_fraction:
        passed = False
        issues.append(f"Excessive shadow clipping ({under_frac * 100:.1f}% > {max_underexposure_fraction * 100:.1f}%)")

    if over_frac > max_overexposure_fraction:
        passed = False
        issues.append(f"Excessive highlight clipping ({over_frac * 100:.1f}% > {max_overexposure_fraction * 100:.1f}%)")

    if passed:
        explanation = f"Optimal illumination and dynamic range (mean luma: {mean_luma:.1f}/255)."
    else:
        explanation = "; ".join(issues)

    return ExposureMetricResult(
        mean_luminance=mean_luma,
        underexposed_fraction=under_frac,
        overexposed_fraction=over_frac,
        dynamic_range=dynamic_range,
        passed=passed,
        explanation=explanation,
    )
