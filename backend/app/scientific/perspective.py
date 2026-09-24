"""REACTRA V2 — Perspective Normalization & Canonical Warping.

Warps detected quadrilateral corners to canonical card dimensions using OpenCV homography.
Section References: PRD V2 §12, Master Build Spec §12.
"""

from typing import Tuple
import cv2
import numpy as np


class PerspectiveResult:
    """Container for normalized warped image and transform matrix."""
    def __init__(
        self,
        warped_rgb: np.ndarray,
        transform_matrix: np.ndarray,
        canonical_width: int,
        canonical_height: int,
    ):
        self.warped_rgb = warped_rgb
        self.transform_matrix = transform_matrix
        self.canonical_width = canonical_width
        self.canonical_height = canonical_height


def normalize_card_perspective(
    rgb_image: np.ndarray,
    ordered_corners: np.ndarray,  # Shape (4, 2) [TL, TR, BR, BL]
    canonical_width: int = 600,
    canonical_height: int = 400,
) -> PerspectiveResult:
    """Apply 4-point perspective transform to map detected card to canonical coordinates.
    
    Parameters
    ----------
    rgb_image : np.ndarray
        Source RGB image.
    ordered_corners : np.ndarray
        4 clockwise (x, y) corners [TL, TR, BR, BL].
    canonical_width, canonical_height : int
        Destination dimensions in pixels.
        
    Returns
    -------
    PerspectiveResult
    """
    src_pts = ordered_corners.astype(np.float32)
    dst_pts = np.array([
        [0.0, 0.0],
        [float(canonical_width - 1), 0.0],
        [float(canonical_width - 1), float(canonical_height - 1)],
        [0.0, float(canonical_height - 1)],
    ], dtype=np.float32)

    # Compute perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Apply perspective warp
    warped_rgb = cv2.warpPerspective(
        rgb_image,
        M,
        (canonical_width, canonical_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )

    return PerspectiveResult(
        warped_rgb=warped_rgb,
        transform_matrix=M,
        canonical_width=canonical_width,
        canonical_height=canonical_height,
    )
