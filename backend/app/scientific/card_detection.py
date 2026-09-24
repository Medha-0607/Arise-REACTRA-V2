"""REACTRA V2 — Reference Card Detection & Geometric Filtering.

Detects candidate reference-card quadrilaterals, orders 4 corners,
measures aspect ratio and skew angle.
Section References: PRD V2 §12, Master Build Spec §12.
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np


class CardDetectionResult:
    """Diagnostic container for reference card localization."""
    def __init__(
        self,
        detected: bool,
        corners: Optional[np.ndarray],  # Shape (4, 2) [TL, TR, BR, BL]
        confidence: float,
        aspect_ratio: float,
        skew_angle_deg: float,
        area_fraction: float,
        reason: str,
    ):
        self.detected = detected
        self.corners = corners
        self.confidence = confidence
        self.aspect_ratio = aspect_ratio
        self.skew_angle_deg = skew_angle_deg
        self.area_fraction = area_fraction
        self.reason = reason


def order_corners(pts: np.ndarray) -> np.ndarray:
    """Order 4 (x, y) coordinates clockwise: Top-Left, Top-Right, Bottom-Right, Bottom-Left."""
    pts = pts.reshape(4, 2).astype(np.float32)
    ordered = np.zeros((4, 2), dtype=np.float32)

    # Sum: x + y -> Top-Left is smallest sum, Bottom-Right is largest sum
    s = pts.sum(axis=1)
    ordered[0] = pts[np.argmin(s)]  # Top-Left
    ordered[2] = pts[np.argmax(s)]  # Bottom-Right

    # Difference: y - x -> Top-Right is smallest difference, Bottom-Left is largest difference
    diff = np.diff(pts, axis=1)
    ordered[1] = pts[np.argmin(diff)]  # Top-Right
    ordered[3] = pts[np.argmax(diff)]  # Bottom-Left

    return ordered


def calculate_skew_angle(corners: np.ndarray) -> float:
    """Calculate the absolute horizontal skew angle of the top edge in degrees."""
    tl, tr = corners[0], corners[1]
    dx = tr[0] - tl[0]
    dy = tr[1] - tl[1]
    if dx == 0:
        return 90.0
    angle_rad = np.arctan2(abs(dy), abs(dx))
    return float(np.degrees(angle_rad))


def detect_reference_card(
    rgb_image: np.ndarray,
    target_aspect_ratio: float = 1.5,
    aspect_ratio_tolerance: float = 0.45,
    min_area_fraction: float = 0.08,
) -> CardDetectionResult:
    """Locate reference card quadrilateral within an RGB image.
    
    Parameters
    ----------
    rgb_image : np.ndarray
        Source RGB image.
    target_aspect_ratio : float
        Expected card width / height ratio (e.g. 600/400 = 1.5).
    aspect_ratio_tolerance : float
        Allowed deviation from target aspect ratio.
    min_area_fraction : float
        Minimum fraction of frame area the card must occupy.
        
    Returns
    -------
    CardDetectionResult
    """
    img_h, img_w = rgb_image.shape[:2]
    total_area = float(img_w * img_h)

    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    
    # 1. Multi-scale edge & contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    threshold_pairs = [(50, 150), (30, 100), (80, 200)]
    best_candidate = None
    best_score = -1.0

    for low_t, high_t in threshold_pairs:
        edges = cv2.Canny(blurred, low_t, high_t)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        for c in contours:
            area = cv2.contourArea(c)
            area_frac = area / total_area
            if area_frac < min_area_fraction:
                continue

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.025 * peri, True)

            if len(approx) == 4 and cv2.isContourConvex(approx):
                corners = order_corners(approx)
                tl, tr, br, bl = corners
                width_top = np.linalg.norm(tr - tl)
                width_bot = np.linalg.norm(br - bl)
                height_left = np.linalg.norm(bl - tl)
                height_right = np.linalg.norm(br - tr)
                
                avg_w = (width_top + width_bot) / 2.0
                avg_h = (height_left + height_right) / 2.0
                if avg_h <= 1.0:
                    continue
                
                detected_ratio = avg_w / avg_h
                ratio_diff = abs(detected_ratio - target_aspect_ratio)
                
                if ratio_diff <= aspect_ratio_tolerance:
                    score = area_frac * (1.0 - (ratio_diff / aspect_ratio_tolerance) * 0.5)
                    if score > best_score:
                        best_score = score
                        best_candidate = (corners, detected_ratio, area_frac)

    # 2. Check if a high-confidence card was detected
    if best_candidate is not None:
        corners, aspect_ratio, area_fraction = best_candidate
        skew_angle = calculate_skew_angle(corners)
        confidence = min(1.0, max(0.0, float(best_score / 0.5)))
        return CardDetectionResult(
            detected=True,
            corners=corners,
            confidence=confidence,
            aspect_ratio=float(aspect_ratio),
            skew_angle_deg=skew_angle,
            area_fraction=float(area_fraction),
            reason="Reference card quadrilateral successfully localized.",
        )

    # Card detection failure
    frame_ratio = float(img_w) / float(img_h)
    return CardDetectionResult(
        detected=False,
        corners=None,
        confidence=0.0,
        aspect_ratio=frame_ratio,
        skew_angle_deg=0.0,
        area_fraction=0.0,
        reason="No valid reference card quadrilateral detected in image.",
    )
