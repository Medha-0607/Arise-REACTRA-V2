"""REACTRA V2 — Blur Quality Analysis.

Computes Laplacian variance to measure high-frequency edge sharpness.
Section References: PRD V2 §10, Master Build Spec §10.
"""

from typing import Dict, Any
import cv2
import numpy as np


class BlurMetricResult:
    """Diagnostic container for image blur analysis."""
    def __init__(
        self,
        variance: float,
        threshold: float,
        passed: bool,
        explanation: str,
    ):
        self.variance = variance
        self.threshold = threshold
        self.passed = passed
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variance": round(self.variance, 2),
            "threshold": self.threshold,
            "passed": self.passed,
            "explanation": self.explanation,
        }


def evaluate_blur(
    rgb_image: np.ndarray,
    min_variance_threshold: float = 120.0,
) -> BlurMetricResult:
    """Calculate the focus blur metric using the variance of the Laplacian.
    
    Parameters
    ----------
    rgb_image : np.ndarray
        RGB image (either raw or canonical card).
    min_variance_threshold : float
        Minimum acceptable Laplacian variance.
        
    Returns
    -------
    BlurMetricResult
    """
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = float(laplacian.var())

    passed = variance >= min_variance_threshold
    if passed:
        explanation = (
            f"Focus sharpness acceptable (Laplacian variance: {variance:.1f} >= {min_variance_threshold:.1f})."
        )
    else:
        explanation = (
            f"Excessive motion or focus blur detected (Laplacian variance: {variance:.1f} < {min_variance_threshold:.1f})."
        )

    return BlurMetricResult(
        variance=variance,
        threshold=min_variance_threshold,
        passed=passed,
        explanation=explanation,
    )
