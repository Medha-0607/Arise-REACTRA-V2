"""REACTRA V2 — Robust Color Estimation & Statistical Aggregation.

Filters glare/noise pixels and computes robust central tendency and dispersion metrics
in calibrated CIE L*a*b* color space.
Section References: PRD V2 §14, Master Build Spec §14.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from app.scientific.color import rgb_to_lab
from app.scientific.calibration import CalibrationResult
from app.scientific.roi import ExtractedRoi


class WellColorMeasurement:
    """Robust colorimetric measurement for a single reaction well."""
    def __init__(
        self,
        roi_id: str,
        name: str,
        bbox: Tuple[int, int, int, int],
        sampled_bbox: Tuple[int, int, int, int],
        valid_pixel_count: int,
        glare_pixel_count: int,
        raw_lab_median: Tuple[float, float, float],
        calibrated_lab_median: Tuple[float, float, float],
        calibrated_lab_trimmed_mean: Tuple[float, float, float],
        lab_std_dev: Tuple[float, float, float],
        is_valid: bool,
        rejection_reason: Optional[str] = None,
    ):
        self.roi_id = roi_id
        self.name = name
        self.bbox = bbox
        self.sampled_bbox = sampled_bbox
        self.valid_pixel_count = valid_pixel_count
        self.glare_pixel_count = glare_pixel_count
        self.raw_lab_median = raw_lab_median
        self.calibrated_lab_median = calibrated_lab_median
        self.calibrated_lab_trimmed_mean = calibrated_lab_trimmed_mean
        self.lab_std_dev = lab_std_dev
        self.is_valid = is_valid
        self.rejection_reason = rejection_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roi_id": self.roi_id,
            "name": self.name,
            "bbox": list(self.bbox),
            "sampled_bbox": list(self.sampled_bbox),
            "valid_pixel_count": self.valid_pixel_count,
            "glare_pixel_count": self.glare_pixel_count,
            "raw_lab_median": [round(float(v), 2) for v in self.raw_lab_median],
            "calibrated_lab_median": [round(float(v), 2) for v in self.calibrated_lab_median],
            "calibrated_lab_trimmed_mean": [round(float(v), 2) for v in self.calibrated_lab_trimmed_mean],
            "lab_std_dev": [round(float(v), 2) for v in self.lab_std_dev],
            "is_valid": self.is_valid,
            "rejection_reason": self.rejection_reason,
        }


def robust_estimate_well_color(
    extracted_roi: ExtractedRoi,
    glare_mask: np.ndarray,  # 2D uint8 mask for canonical card
    calibration: Optional[CalibrationResult] = None,
    min_valid_pixels: int = 50,
    trim_fraction: float = 0.10,
) -> WellColorMeasurement:
    """Extract and estimate robust central tendency in calibrated CIE L*a*b* for a reaction well.
    
    Parameters
    ----------
    extracted_roi : ExtractedRoi
        Sampled ROI pixel crop.
    glare_mask : np.ndarray
        Full canonical card glare mask.
    calibration : CalibrationResult, optional
        Illumination calibration model to apply.
    min_valid_pixels : int
        Minimum required valid (non-glare) pixels.
    trim_fraction : float
        Fraction of extreme pixels to trim for trimmed mean.
        
    Returns
    -------
    WellColorMeasurement
    """
    sx, sy, sw, sh = extracted_roi.sampled_bbox
    crop_h, crop_w = extracted_roi.rgb_crop.shape[:2]

    # Extract corresponding sub-mask from glare mask
    glare_submask = glare_mask[sy:sy + crop_h, sx:sx + crop_w]
    
    # Valid pixels: ROI mask is active (255) AND glare mask is clear (0)
    valid_mask = (extracted_roi.mask == 255) & (glare_submask == 0)
    
    valid_count = int(np.count_nonzero(valid_mask))
    glare_count = int(np.count_nonzero(glare_submask == 255))

    if valid_count < min_valid_pixels:
        # Rejection: insufficient valid pixels
        return WellColorMeasurement(
            roi_id=extracted_roi.roi_id,
            name=extracted_roi.name,
            bbox=extracted_roi.original_bbox,
            sampled_bbox=extracted_roi.sampled_bbox,
            valid_pixel_count=valid_count,
            glare_pixel_count=glare_count,
            raw_lab_median=(0.0, 0.0, 0.0),
            calibrated_lab_median=(0.0, 0.0, 0.0),
            calibrated_lab_trimmed_mean=(0.0, 0.0, 0.0),
            lab_std_dev=(0.0, 0.0, 0.0),
            is_valid=False,
            rejection_reason=(
                f"Insufficient valid pixels in reaction zone ({valid_count} < {min_valid_pixels}). "
                "Excessive glare or occlusion."
            ),
        )

    # Convert valid pixels to CIE L*a*b*
    valid_rgb = extracted_roi.rgb_crop[valid_mask]  # Shape (N, 3)
    valid_raw_lab = rgb_to_lab(valid_rgb)  # Shape (N, 3)

    # Raw median
    raw_median = np.median(valid_raw_lab, axis=0)

    # Apply calibration if provided
    if calibration is not None and calibration.passed:
        valid_calib_lab = calibration.apply_calibration(valid_raw_lab)
    else:
        valid_calib_lab = valid_raw_lab.copy()

    # Robust metrics on calibrated LAB
    calib_median = np.median(valid_calib_lab, axis=0)

    # 10% Trimmed Mean
    low_idx = int(valid_count * trim_fraction)
    high_idx = max(low_idx + 1, int(valid_count * (1.0 - trim_fraction)))
    
    # Sort per channel for trimmed mean
    trimmed_means = []
    for ch in range(3):
        sorted_ch = np.sort(valid_calib_lab[:, ch])
        trimmed_means.append(float(np.mean(sorted_ch[low_idx:high_idx])))

    # Standard deviation per channel
    std_devs = np.std(valid_calib_lab, axis=0)

    return WellColorMeasurement(
        roi_id=extracted_roi.roi_id,
        name=extracted_roi.name,
        bbox=extracted_roi.original_bbox,
        sampled_bbox=extracted_roi.sampled_bbox,
        valid_pixel_count=valid_count,
        glare_pixel_count=glare_count,
        raw_lab_median=tuple(raw_median),
        calibrated_lab_median=tuple(calib_median),
        calibrated_lab_trimmed_mean=tuple(trimmed_means),
        lab_std_dev=tuple(std_devs),
        is_valid=True,
        rejection_reason=None,
    )
