"""REACTRA V2 — Reference Card Calibration & Illumination Correction.

Samples reference color patches, computes least-squares affine color correction matrix,
and evaluates mean Delta E76 residual error.
Section References: PRD V2 §13, Master Build Spec §13.
"""

from typing import Dict, List, Tuple, Any
import numpy as np

from app.scientific.color import rgb_to_lab, delta_e_76
from app.scientific.profiles import CalibrationPatchDef


class CalibrationResult:
    """Diagnostic container for reference card illumination calibration."""
    def __init__(
        self,
        passed: bool,
        mean_delta_e: float,
        threshold: float,
        affine_matrix: np.ndarray,  # 3x4 affine matrix
        patch_diagnostics: Dict[str, Dict[str, Any]],
        explanation: str,
    ):
        self.passed = passed
        self.mean_delta_e = mean_delta_e
        self.threshold = threshold
        self.affine_matrix = affine_matrix
        self.patch_diagnostics = patch_diagnostics
        self.explanation = explanation

    def apply_calibration(self, lab_vector: np.ndarray) -> np.ndarray:
        """Apply affine calibration correction to a single [L*, a*, b*] vector or array."""
        lab = np.asarray(lab_vector, dtype=np.float64)
        if lab.ndim == 1:
            homog = np.array([lab[0], lab[1], lab[2], 1.0], dtype=np.float64)
            return np.dot(self.affine_matrix, homog)
        elif lab.ndim == 2:
            ones = np.ones((lab.shape[0], 1), dtype=np.float64)
            homog = np.hstack([lab, ones])
            return np.dot(homog, self.affine_matrix.T)
        else:
            orig_shape = lab.shape
            reshaped = lab.reshape(-1, 3)
            ones = np.ones((reshaped.shape[0], 1), dtype=np.float64)
            homog = np.hstack([reshaped, ones])
            calibrated = np.dot(homog, self.affine_matrix.T)
            return calibrated.reshape(orig_shape)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "mean_delta_e": round(self.mean_delta_e, 2),
            "threshold": self.threshold,
            "explanation": self.explanation,
            "patch_count": len(self.patch_diagnostics),
            "patch_diagnostics": self.patch_diagnostics,
        }


def calibrate_reference_card(
    canonical_card_rgb: np.ndarray,
    patch_definitions: List[CalibrationPatchDef],
    max_delta_e_threshold: float = 18.0,
    patch_inset_px: int = 4,
) -> CalibrationResult:
    """Calibrate color and illumination using reference patches on canonical card.
    
    Parameters
    ----------
    canonical_card_rgb : np.ndarray
        Perspective-normalized RGB card image (e.g. 600x400).
    patch_definitions : List[CalibrationPatchDef]
        List of reference patches with coordinates and nominal CIE L*a*b* values.
    max_delta_e_threshold : float
        Maximum allowed average Delta E76 residual.
    patch_inset_px : int
        Pixel margin to inset inside patch bbox to avoid patch boundary artifacts.
        
    Returns
    -------
    CalibrationResult
    """
    card_h, card_w = canonical_card_rgb.shape[:2]
    
    observed_lab_list = []
    nominal_lab_list = []
    patch_diagnostics: Dict[str, Dict[str, Any]] = {}

    for patch in patch_definitions:
        px, py, pw, ph = patch.bbox
        # Inset to sample pure patch center
        x1 = max(0, px + patch_inset_px)
        y1 = max(0, py + patch_inset_px)
        x2 = min(card_w, px + pw - patch_inset_px)
        y2 = min(card_h, py + ph - patch_inset_px)

        if x2 <= x1 or y2 <= y1:
            continue

        patch_crop = canonical_card_rgb[y1:y2, x1:x2]
        # Convert crop to CIE L*a*b*
        patch_lab_pixels = rgb_to_lab(patch_crop).reshape(-1, 3)
        
        # Robust spatial median for patch observed color
        observed_lab = np.median(patch_lab_pixels, axis=0)
        nominal_lab = np.array(patch.nominal_lab, dtype=np.float64)

        observed_lab_list.append(observed_lab)
        nominal_lab_list.append(nominal_lab)

        raw_delta_e = delta_e_76(observed_lab, nominal_lab)
        patch_diagnostics[patch.patch_id] = {
            "name": patch.name,
            "nominal_lab": [round(float(v), 2) for v in nominal_lab],
            "observed_lab": [round(float(v), 2) for v in observed_lab],
            "raw_delta_e": round(raw_delta_e, 2),
        }

    if len(observed_lab_list) < 3:
        # Insufficient patches
        identity_3x4 = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ], dtype=np.float64)
        return CalibrationResult(
            passed=False,
            mean_delta_e=999.0,
            threshold=max_delta_e_threshold,
            affine_matrix=identity_3x4,
            patch_diagnostics=patch_diagnostics,
            explanation="Insufficient reference calibration patches available for estimation.",
        )

    # Solve least-squares affine transformation:
    # Target = Observed_Homog * M_T  ==>  M_T = (Observed_Homog)^+ * Target
    obs_mat = np.array(observed_lab_list, dtype=np.float64)  # Shape (N, 3)
    nom_mat = np.array(nominal_lab_list, dtype=np.float64)   # Shape (N, 3)

    ones = np.ones((obs_mat.shape[0], 1), dtype=np.float64)
    obs_homog = np.hstack([obs_mat, ones])  # Shape (N, 4)

    # Least-squares fit
    M_T, residuals, rank, s = np.linalg.lstsq(obs_homog, nom_mat, rcond=None)
    affine_3x4 = M_T.T  # Shape (3, 4)

    # Compute calibrated patch values and residuals
    calibrated_patches = np.dot(obs_homog, M_T)
    delta_es = []
    for i, patch in enumerate(patch_definitions):
        if patch.patch_id in patch_diagnostics:
            calib_lab = calibrated_patches[i]
            d_e = delta_e_76(calib_lab, nominal_lab_list[i])
            delta_es.append(d_e)
            patch_diagnostics[patch.patch_id]["calibrated_lab"] = [round(float(v), 2) for v in calib_lab]
            patch_diagnostics[patch.patch_id]["residual_delta_e"] = round(d_e, 2)

    mean_residual_delta_e = float(np.mean(delta_es)) if delta_es else 999.0
    passed = mean_residual_delta_e <= max_delta_e_threshold

    if passed:
        explanation = (
            f"Color calibration successful (mean residual Delta E: {mean_residual_delta_e:.1f} <= {max_delta_e_threshold:.1f})."
        )
    else:
        explanation = (
            f"Reference card color calibration residual exceeded limit ({mean_residual_delta_e:.1f} > {max_delta_e_threshold:.1f}). "
            "Illumination spectrum non-linear or card damaged."
        )

    return CalibrationResult(
        passed=passed,
        mean_delta_e=mean_residual_delta_e,
        threshold=max_delta_e_threshold,
        affine_matrix=affine_3x4,
        patch_diagnostics=patch_diagnostics,
        explanation=explanation,
    )
