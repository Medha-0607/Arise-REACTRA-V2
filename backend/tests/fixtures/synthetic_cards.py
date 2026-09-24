"""REACTRA V2 — Synthetic Test Fixtures for Scientific Pipeline Testing.

All images generated here are explicitly labelled: TEST FIXTURE.
They serve strictly for automated quality guard verification and pipeline testing.
"""

from typing import Tuple
import cv2
import numpy as np


def generate_valid_card(
    width: int = 600,
    height: int = 400,
    reaction_rgb: Tuple[int, int, int] = (128, 0, 128),  # Purple reaction
) -> np.ndarray:
    """Generate a clean, high-contrast synthetic reference card (TEST FIXTURE)."""
    img = np.full((height, width, 3), 220, dtype=np.uint8)  # Light neutral background

    # Outer border (black)
    cv2.rectangle(img, (10, 10), (width - 10, height - 10), (20, 20, 20), 4)

    # Add TEST FIXTURE banner
    cv2.putText(
        img,
        "REACTRA TEST FIXTURE -- SYNTHETIC CARD",
        (40, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (40, 40, 40),
        1,
        cv2.LINE_AA,
    )

    # 6 Reference Calibration Patches (Y=30 to Y=90)
    # 1. White (L*=95)
    cv2.rectangle(img, (40, 30), (100, 90), (245, 245, 245), -1)
    cv2.rectangle(img, (40, 30), (100, 90), (50, 50, 50), 1)

    # 2. Light Gray (L*=70)
    cv2.rectangle(img, (130, 30), (190, 90), (178, 178, 178), -1)
    cv2.rectangle(img, (130, 30), (190, 90), (50, 50, 50), 1)

    # 3. Mid Gray (L*=50)
    cv2.rectangle(img, (220, 30), (280, 90), (128, 128, 128), -1)
    cv2.rectangle(img, (220, 30), (280, 90), (50, 50, 50), 1)

    # 4. Black (L*=10)
    cv2.rectangle(img, (310, 30), (370, 90), (25, 25, 25), -1)
    cv2.rectangle(img, (310, 30), (370, 90), (50, 50, 50), 1)

    # 5. Cyan Patch (RGB: 0, 180, 200)
    cv2.rectangle(img, (400, 30), (460, 90), (0, 180, 200), -1)
    cv2.rectangle(img, (400, 30), (460, 90), (50, 50, 50), 1)

    # 6. Magenta Patch (RGB: 200, 40, 150)
    cv2.rectangle(img, (490, 30), (550, 90), (200, 40, 150), -1)
    cv2.rectangle(img, (490, 30), (550, 90), (50, 50, 50), 1)

    # Reaction Wells
    # Well 1: Primary Reaction Well (Left: X=80..200, Y=180..300)
    cv2.circle(img, (140, 240), 55, (80, 80, 80), 2)
    cv2.circle(img, (140, 240), 50, reaction_rgb, -1)

    # Well 2: Negative Control Well (Right: X=400..520, Y=180..300)
    cv2.circle(img, (460, 240), 55, (80, 80, 80), 2)
    cv2.circle(img, (460, 240), 50, (230, 230, 220), -1)

    # High frequency details to ensure sharpness
    cv2.putText(img, "W1: REACTION", (95, 315), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 20, 20), 1)
    cv2.putText(img, "W2: CONTROL", (420, 315), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 20, 20), 1)

    return img


def generate_blurred_card() -> np.ndarray:
    """Generate a blurred card fixture with low Laplacian variance (TEST FIXTURE)."""
    valid = generate_valid_card()
    # Apply severe Gaussian blur
    return cv2.GaussianBlur(valid, (25, 25), 0)


def generate_glare_card() -> np.ndarray:
    """Generate a card with intense specular reflection on reaction well (TEST FIXTURE)."""
    card = generate_valid_card()
    # Add intense white specular highlight in reaction well 1 (center 140, 240)
    cv2.circle(card, (140, 240), 30, (255, 255, 255), -1)
    return card


def generate_underexposed_card() -> np.ndarray:
    """Generate an underexposed card fixture (mean luma < 30) (TEST FIXTURE)."""
    card = generate_valid_card()
    return (card.astype(np.float32) * 0.10).astype(np.uint8)


def generate_overexposed_card() -> np.ndarray:
    """Generate an overexposed card fixture (mean luma > 230) (TEST FIXTURE)."""
    card = generate_valid_card()
    return np.clip(card.astype(np.float32) * 1.5 + 80, 0, 255).astype(np.uint8)


def generate_missing_card() -> np.ndarray:
    """Generate a background texture with no reference card (TEST FIXTURE)."""
    return np.random.randint(50, 150, (400, 600, 3), dtype=np.uint8)


def generate_skewed_card() -> np.ndarray:
    """Generate a card placed in a larger frame with perspective keystone distortion (TEST FIXTURE)."""
    card = generate_valid_card(400, 260)
    # Embed inside 800x600 canvas with severe perspective warp
    canvas = np.full((600, 800, 3), 40, dtype=np.uint8)
    
    src_pts = np.array([
        [0.0, 0.0],
        [400.0, 0.0],
        [400.0, 260.0],
        [0.0, 260.0],
    ], dtype=np.float32)

    dst_pts = np.array([
        [150.0, 100.0],
        [650.0, 180.0],
        [580.0, 520.0],
        [100.0, 460.0],
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(card, M, (800, 600))
    
    # Composite into canvas
    mask = cv2.warpPerspective(np.ones((260, 400), dtype=np.uint8) * 255, M, (800, 600))
    canvas[mask == 255] = warped[mask == 255]
    return canvas
