"""REACTRA V2 — Reaction Region of Interest (ROI) Extraction.

Extracts profile-defined reaction well sampling regions with spatial erosion margins.
Section References: PRD V2 §14, Master Build Spec §14.
"""

from typing import Dict, List, Tuple
import cv2
import numpy as np
from app.scientific.profiles import ReactionRoiDef


class ExtractedRoi:
    """Container for sampled reaction well pixel region."""
    def __init__(
        self,
        roi_id: str,
        name: str,
        original_bbox: Tuple[int, int, int, int],
        sampled_bbox: Tuple[int, int, int, int],
        rgb_crop: np.ndarray,
        mask: np.ndarray,  # 2D uint8 mask (255 = in sampling zone)
    ):
        self.roi_id = roi_id
        self.name = name
        self.original_bbox = original_bbox
        self.sampled_bbox = sampled_bbox
        self.rgb_crop = rgb_crop
        self.mask = mask


def extract_reaction_rois(
    canonical_card_rgb: np.ndarray,
    roi_definitions: List[ReactionRoiDef],
) -> List[ExtractedRoi]:
    """Extract profile-defined reaction ROIs with spatial erosion margins.
    
    Parameters
    ----------
    canonical_card_rgb : np.ndarray
        Perspective-normalized RGB card image (e.g. 600x400).
    roi_definitions : List[ReactionRoiDef]
        List of reaction well definitions with bounding boxes and margins.
        
    Returns
    -------
    List[ExtractedRoi]
    """
    card_h, card_w = canonical_card_rgb.shape[:2]
    extracted_list: List[ExtractedRoi] = []

    for roi_def in roi_definitions:
        rx, ry, rw, rh = roi_def.bbox
        margin = roi_def.inset_margin_px

        # Calculate eroded sampling bounds to avoid pouch edges
        x1 = max(0, rx + margin)
        y1 = max(0, ry + margin)
        x2 = min(card_w, rx + rw - margin)
        y2 = min(card_h, ry + rh - margin)

        if x2 <= x1 or y2 <= y1:
            continue

        rgb_crop = canonical_card_rgb[y1:y2, x1:x2].copy()
        
        # Elliptical / rectangular mask for sampling zone
        mask = np.full((y2 - y1, x2 - x1), 255, dtype=np.uint8)

        extracted_list.append(
            ExtractedRoi(
                roi_id=roi_def.roi_id,
                name=roi_def.name,
                original_bbox=roi_def.bbox,
                sampled_bbox=(x1, y1, x2 - x1, y2 - y1),
                rgb_crop=rgb_crop,
                mask=mask,
            )
        )

    return extracted_list
