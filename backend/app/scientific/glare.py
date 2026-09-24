"""REACTRA V2 — Specular Glare & Reflection Rejection.

Detects specular highlights within reaction regions of interest to prevent
reflection contamination from distorting color extraction.
Section References: PRD V2 §10, Master Build Spec §10.
"""

from typing import Dict, List, Tuple, Any
import cv2
import numpy as np


class GlareMetricResult:
    """Diagnostic container for specular reflection analysis."""
    def __init__(
        self,
        glare_mask: np.ndarray,  # 2D uint8 mask (255 = glare, 0 = clear)
        max_roi_glare_fraction: float,
        threshold: float,
        passed: bool,
        explanation: str,
        roi_glare_fractions: Dict[str, float],
    ):
        self.glare_mask = glare_mask
        self.max_roi_glare_fraction = max_roi_glare_fraction
        self.threshold = threshold
        self.passed = passed
        self.explanation = explanation
        self.roi_glare_fractions = roi_glare_fractions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_roi_glare_fraction": round(self.max_roi_glare_fraction, 4),
            "threshold": self.threshold,
            "passed": self.passed,
            "explanation": self.explanation,
            "roi_glare_fractions": {k: round(v, 4) for k, v in self.roi_glare_fractions.items()},
        }


def detect_specular_glare(
    rgb_image: np.ndarray,
    reaction_rois: List[Tuple[str, Tuple[int, int, int, int]]],  # List of (roi_id, (x, y, w, h))
    max_glare_fraction: float = 0.05,
    luminance_threshold: int = 248,
    saturation_threshold: int = 35,
) -> GlareMetricResult:
    """Detect specular reflections in RGB image and evaluate reaction ROI coverage.
    
    Parameters
    ----------
    rgb_image : np.ndarray
        Canonical card RGB image.
    reaction_rois : List[Tuple[str, Tuple[int, int, int, int]]]
        List of ROI identifiers and bounding boxes [x, y, w, h].
    max_glare_fraction : float
        Maximum allowed fraction of any reaction ROI covered by glare.
    luminance_threshold : int
        Luminance cutoff above which pixels are potential specular highlights.
    saturation_threshold : int
        Maximum saturation cutoff (glare is typically desaturated white).
        
    Returns
    -------
    GlareMetricResult
    """
    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    # Glare condition: High Value/Luminance AND Low Saturation, OR pure saturated white (gray >= 252)
    glare_condition = ((val >= luminance_threshold) & (sat <= saturation_threshold)) | (gray >= 252)
    glare_mask = np.zeros(gray.shape, dtype=np.uint8)
    glare_mask[glare_condition] = 255

    roi_fractions: Dict[str, float] = {}
    max_frac = 0.0

    for roi_id, (rx, ry, rw, rh) in reaction_rois:
        # Constrain to image bounds
        img_h, img_w = gray.shape[:2]
        x1, y1 = max(0, rx), max(0, ry)
        x2, y2 = min(img_w, rx + rw), min(img_h, ry + rh)
        
        roi_submask = glare_mask[y1:y2, x1:x2]
        roi_total_pixels = float(roi_submask.size)
        if roi_total_pixels > 0:
            roi_glare_pixels = float(np.count_nonzero(roi_submask))
            frac = roi_glare_pixels / roi_total_pixels
        else:
            frac = 0.0

        roi_fractions[roi_id] = frac
        if frac > max_frac:
            max_frac = frac

    passed = max_frac <= max_glare_fraction
    if passed:
        explanation = (
            f"Specular glare minimal (max ROI glare: {max_frac * 100:.1f}% <= {max_glare_fraction * 100:.1f}%)."
        )
    else:
        explanation = (
            f"Excessive specular glare detected in reaction zone ({max_frac * 100:.1f}% > {max_glare_fraction * 100:.1f}%). "
            "Diffuse lighting required."
        )

    return GlareMetricResult(
        glare_mask=glare_mask,
        max_roi_glare_fraction=max_frac,
        threshold=max_glare_fraction,
        passed=passed,
        explanation=explanation,
        roi_glare_fractions=roi_fractions,
    )
