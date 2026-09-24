"""REACTRA V2 — Scientific Color Space Conversion & Delta-E Metrics.

Converts standard sRGB to illumination-invariant CIE L*a*b* (CIE D65/2°)
and computes Delta E76 color distance metrics.
Section References: PRD V2 §13, Master Build Spec §13.
"""

from typing import Tuple, Union
import numpy as np


def srgb_to_linear_rgb(srgb: np.ndarray) -> np.ndarray:
    """Convert gamma-corrected sRGB [0, 1] to linear RGB."""
    mask = srgb > 0.04045
    linear = np.zeros_like(srgb, dtype=np.float64)
    linear[mask] = np.power((srgb[mask] + 0.055) / 1.055, 2.4)
    linear[~mask] = srgb[~mask] / 12.92
    return linear


def linear_rgb_to_xyz(linear_rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB to CIE XYZ (D65 standard illuminant)."""
    # sRGB to XYZ matrix (D65, 2-degree observer)
    M = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ], dtype=np.float64)
    return np.dot(linear_rgb, M.T)


def xyz_to_lab(xyz: np.ndarray) -> np.ndarray:
    """Convert CIE XYZ to CIE L*a*b* (Reference White: D65 Xn=0.95047, Yn=1.00000, Zn=1.08883)."""
    # D65 reference white points
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    
    x_rel = xyz[..., 0] / Xn
    y_rel = xyz[..., 1] / Yn
    z_rel = xyz[..., 2] / Zn

    epsilon = 0.008856  # (6/29)^3
    kappa = 903.3       # (29/3)^3

    def f(t: np.ndarray) -> np.ndarray:
        mask = t > epsilon
        out = np.zeros_like(t, dtype=np.float64)
        out[mask] = np.cbrt(t[mask])
        out[~mask] = (kappa * t[~mask] + 16.0) / 116.0
        return out

    fx = f(x_rel)
    fy = f(y_rel)
    fz = f(z_rel)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return np.stack([L, a, b], axis=-1)


def rgb_to_lab(rgb_array: np.ndarray) -> np.ndarray:
    """Convert standard uint8 or float [0, 1] RGB array to standard CIE L*a*b*.
    
    L* is in range [0, 100], a* in [-128, 127], b* in [-128, 127].
    """
    if rgb_array.dtype == np.uint8:
        norm_rgb = rgb_array.astype(np.float64) / 255.0
    else:
        norm_rgb = np.clip(rgb_array.astype(np.float64), 0.0, 1.0)

    linear_rgb = srgb_to_linear_rgb(norm_rgb)
    xyz = linear_rgb_to_xyz(linear_rgb)
    return xyz_to_lab(xyz)


def delta_e_76(lab1: Union[np.ndarray, Tuple[float, float, float]], lab2: Union[np.ndarray, Tuple[float, float, float]]) -> float:
    """Calculate CIE76 Euclidean color distance Delta E76.
    
    Delta E = sqrt((L1 - L2)^2 + (a1 - a2)^2 + (b1 - b2)^2)
    """
    l1 = np.asarray(lab1, dtype=np.float64)
    l2 = np.asarray(lab2, dtype=np.float64)
    diff = l1 - l2
    return float(np.sqrt(np.sum(diff ** 2)))
