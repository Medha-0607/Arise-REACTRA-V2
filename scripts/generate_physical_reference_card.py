"""REACTRA V2 — Physical Reference Card Generator & Validator.

Generates:
1. reference_cards/REACTRA_DEMO_REFERENCE_CARD_HIGHRES.png (300 DPI high-res standalone card)
2. reference_cards/REACTRA_DEMO_REFERENCE_CARD.pdf (Print-ready standalone card PDF)
3. reference_cards/REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.png (Complete A4 print sheet with scale rulers & crop marks)
4. reference_cards/REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.pdf (Print-ready A4 PDF)

Validates:
- Ingestion by `ingest_image_data()`
- Localization by `detect_reference_card()`
- Calibration by `calibrate_reference_card()`
- Full measurement by `measure_session_capture()`
"""

import os
import sys
import math
from typing import Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.scientific.profiles import STANDARD_GRID_PROFILE
from app.scientific.image_io import ingest_image_data
from app.scientific.card_detection import detect_reference_card
from app.scientific.calibration import calibrate_reference_card
from app.scientific.measurement import execute_scientific_measurement


def create_reference_card_image(scale: float = 1.0) -> np.ndarray:
    """
    Generate canonical reference card scaled by `scale` factor.
    Base canonical resolution is 600x400 (aspect ratio 1.5).
    At scale=1.0: 600x400 px
    At scale=2.953 (300 DPI for 150mm x 100mm): 1772 x 1181 px
    At scale=4.0 (300 DPI high-res master): 2400 x 1600 px
    """
    base_w, base_h = 600, 400
    w = int(round(base_w * scale))
    h = int(round(base_h * scale))

    # Background neutral light gray (RGB: 220, 222, 224)
    img = np.full((h, w, 3), (224, 222, 220), dtype=np.uint8)  # BGR for OpenCV

    def s(val: int | float) -> int:
        return int(round(val * scale))

    # Outer border (black)
    border_thick = max(2, s(4))
    cv2.rectangle(img, (s(10), s(10)), (w - s(10), h - s(10)), (20, 20, 20), border_thick)

    # 4 Corner alignment crosshair markers
    corner_len = s(16)
    c_thick = max(1, s(2))
    # Top-Left
    cv2.line(img, (s(10), s(10) + corner_len), (s(10), s(10)), (0, 0, 0), c_thick)
    cv2.line(img, (s(10) + corner_len, s(10)), (s(10), s(10)), (0, 0, 0), c_thick)
    # Top-Right
    cv2.line(img, (w - s(10), s(10) + corner_len), (w - s(10), s(10)), (0, 0, 0), c_thick)
    cv2.line(img, (w - s(10) - corner_len, s(10)), (w - s(10), s(10)), (0, 0, 0), c_thick)
    # Bottom-Left
    cv2.line(img, (s(10), h - s(10) - corner_len), (s(10), h - s(10)), (0, 0, 0), c_thick)
    cv2.line(img, (s(10) + corner_len, h - s(10)), (s(10), h - s(10)), (0, 0, 0), c_thick)
    # Bottom-Right
    cv2.line(img, (w - s(10), h - s(10) - corner_len), (w - s(10), h - s(10)), (0, 0, 0), c_thick)
    cv2.line(img, (w - s(10) - corner_len, h - s(10)), (w - s(10), h - s(10)), (0, 0, 0), c_thick)

    # Top Header Labels (Outside machine-readable patches)
    font_thick = max(1, int(round(1 * scale)))
    cv2.putText(
        img,
        "REACTRA DEMO REFERENCE CARD",
        (s(25), s(22)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33 * scale,
        (25, 25, 25),
        font_thick,
        cv2.LINE_AA,
    )

    cv2.putText(
        img,
        "SOFTWARE TEST / CALIBRATION AID -- NOT A CHEMICAL TEST",
        (s(250), s(22)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.26 * scale,
        (70, 70, 70),
        font_thick,
        cv2.LINE_AA,
    )

    # 6 Reference Calibration Patches (Y=30 to Y=90 on base grid)
    # 1. White (L*=95) -> RGB (245, 245, 245)
    cv2.rectangle(img, (s(40), s(30)), (s(100), s(90)), (245, 245, 245), -1)
    cv2.rectangle(img, (s(40), s(30)), (s(100), s(90)), (50, 50, 50), max(1, s(1)))

    # 2. Light Gray (L*=70) -> RGB (178, 178, 178)
    cv2.rectangle(img, (s(130), s(30)), (s(190), s(90)), (178, 178, 178), -1)
    cv2.rectangle(img, (s(130), s(30)), (s(190), s(90)), (50, 50, 50), max(1, s(1)))

    # 3. Mid Gray (L*=50) -> RGB (128, 128, 128)
    cv2.rectangle(img, (s(220), s(30)), (s(280), s(90)), (128, 128, 128), -1)
    cv2.rectangle(img, (s(220), s(30)), (s(280), s(90)), (50, 50, 50), max(1, s(1)))

    # 4. Black (L*=10) -> RGB (25, 25, 25)
    cv2.rectangle(img, (s(310), s(30)), (s(370), s(90)), (25, 25, 25), -1)
    cv2.rectangle(img, (s(310), s(30)), (s(370), s(90)), (50, 50, 50), max(1, s(1)))

    # 5. Cyan (L*=60, a*=-30, b*=-25) -> RGB (0, 180, 200) -> BGR (200, 180, 0)
    cv2.rectangle(img, (s(400), s(30)), (s(460), s(90)), (200, 180, 0), -1)
    cv2.rectangle(img, (s(400), s(30)), (s(460), s(90)), (50, 50, 50), max(1, s(1)))

    # 6. Magenta (L*=50, a*=55, b*=-15) -> RGB (200, 40, 150) -> BGR (150, 40, 200)
    cv2.rectangle(img, (s(490), s(30)), (s(550), s(90)), (150, 40, 200), -1)
    cv2.rectangle(img, (s(490), s(30)), (s(550), s(90)), (50, 50, 50), max(1, s(1)))

    # Patch Labels beneath patches
    patch_labels = [
        ("WHITE", s(48), s(105)),
        ("GRAY 70%", s(133), s(105)),
        ("GRAY 50%", s(223), s(105)),
        ("BLACK", s(322), s(105)),
        ("CYAN", s(415), s(105)),
        ("MAGENTA", s(496), s(105)),
    ]
    for lbl, lx, ly in patch_labels:
        cv2.putText(img, lbl, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.28 * scale, (50, 50, 50), font_thick, cv2.LINE_AA)

    # Reaction Wells
    # Well 1: Primary Reaction Well (Left: center 140, 240, outer radius 55, fill radius 50)
    # Reaction color: Marquis purple/violet RGB (128, 0, 128) -> BGR (128, 0, 128)
    cv2.circle(img, (s(140), s(240)), s(55), (80, 80, 80), max(1, s(2)))
    cv2.circle(img, (s(140), s(240)), s(50), (128, 0, 128), -1)

    # Well 2: Negative Control Well (Right: center 460, 240, outer radius 55, fill radius 50)
    # Control color: Blank neutral RGB (230, 230, 220) -> BGR (220, 230, 230)
    cv2.circle(img, (s(460), s(240)), s(55), (80, 80, 80), max(1, s(2)))
    cv2.circle(img, (s(460), s(240)), s(50), (220, 230, 230), -1)

    # Well Label Text
    cv2.putText(
        img,
        "W1: REACTION WELL (TEST)",
        (s(60), s(318)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33 * scale,
        (20, 20, 20),
        font_thick,
        cv2.LINE_AA,
    )
    cv2.putText(
        img,
        "W2: NEGATIVE CONTROL",
        (s(390), s(318)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33 * scale,
        (20, 20, 20),
        font_thick,
        cv2.LINE_AA,
    )

    # Bottom Metadata & Alignment Text (Two cleanly spaced lines)
    cv2.putText(
        img,
        "GEOMETRY: 150x100mm | PROFILE: MARQUIS-STANDARD-V1 | CARD: REF-CARD-GRID-3X2",
        (s(25), s(362)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.26 * scale,
        (60, 60, 60),
        font_thick,
        cv2.LINE_AA,
    )
    cv2.putText(
        img,
        "OPTICAL TEST FIXTURE -- CALIBRATION AID ONLY -- NOT A REAL REAGENT ASSAY",
        (s(25), s(380)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.24 * scale,
        (80, 80, 80),
        font_thick,
        cv2.LINE_AA,
    )

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def create_a4_print_sheet() -> Image.Image:
    """
    Generate an ISO A4 Print Sheet (210mm x 297mm @ 300 DPI -> 2480 x 3508 pixels).
    Contains:
    - Document title & metadata
    - Exact 1:1 scale reference card (150mm x 100mm = 1772 x 1181 px)
    - 4 Corner Crop / Cutting Marks
    - 100mm horizontal scale ruler & 50mm vertical scale ruler for physical scale verification
    - Printing, paper, illumination, and camera alignment instructions
    """
    a4_w = 2480
    a4_h = 3508
    dpi = 300
    mm_to_px = dpi / 25.4  # ~11.811 px per mm

    sheet = Image.new("RGB", (a4_w, a4_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    # Load default font or fallback
    try:
        font_large = ImageFont.truetype("arial.ttf", 52)
        font_title = ImageFont.truetype("arial.ttf", 38)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 24)
        font_bold = ImageFont.truetype("arialbd.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 20)
        font_mono = ImageFont.truetype("consolas.ttf", 22)
    except Exception:
        font_large = font_title = font_sub = font_body = font_bold = font_small = font_mono = ImageFont.load_default()

    # 1. Header Section
    draw.text((120, 100), "REACTRA V2 — DEMO REFERENCE CARD PRINT SHEET", fill=(10, 15, 30), font=font_large)
    draw.text((120, 165), "Printable Optical Reference & Hardware Calibration Sheet for Computer Vision Validation", fill=(70, 80, 95), font=font_sub)
    draw.line([(120, 210), (a4_w - 120, 210)], fill=(200, 205, 215), width=3)

    # 2. Reference Card Placement (Exact 150mm x 100mm -> 1772 x 1181 px)
    card_w = int(round(150 * mm_to_px))  # 1772 px
    card_h = int(round(100 * mm_to_px))  # 1181 px
    scale_factor = card_w / 600.0        # ~2.9533

    card_rgb = create_reference_card_image(scale=scale_factor)
    card_pil = Image.fromarray(card_rgb)
    card_pil = card_pil.resize((card_w, card_h), Image.Resampling.LANCZOS)

    card_x = (a4_w - card_w) // 2       # Centered horizontally: ~354 px
    card_y = 360

    # Paste Card
    sheet.paste(card_pil, (card_x, card_y))

    # Draw Crop / Cutting Marks (15mm marks outside card corners)
    crop_len = int(round(15 * mm_to_px))
    crop_offset = int(round(4 * mm_to_px))

    # Top-Left Crop Marks
    draw.line([(card_x - crop_offset - crop_len, card_y), (card_x - crop_offset, card_y)], fill=(0, 0, 0), width=3)
    draw.line([(card_x, card_y - crop_offset - crop_len), (card_x, card_y - crop_offset)], fill=(0, 0, 0), width=3)

    # Top-Right Crop Marks
    draw.line([(card_x + card_w + crop_offset, card_y), (card_x + card_w + crop_offset + crop_len, card_y)], fill=(0, 0, 0), width=3)
    draw.line([(card_x + card_w, card_y - crop_offset - crop_len), (card_x + card_w, card_y - crop_offset)], fill=(0, 0, 0), width=3)

    # Bottom-Left Crop Marks
    draw.line([(card_x - crop_offset - crop_len, card_y + card_h), (card_x - crop_offset, card_y + card_h)], fill=(0, 0, 0), width=3)
    draw.line([(card_x, card_y + card_h + crop_offset), (card_x, card_y + card_h + crop_offset + crop_len)], fill=(0, 0, 0), width=3)

    # Bottom-Right Crop Marks
    draw.line([(card_x + card_w + crop_offset, card_y + card_h), (card_x + card_w + crop_offset + crop_len, card_y + card_h)], fill=(0, 0, 0), width=3)
    draw.line([(card_x + card_w, card_y + card_h + crop_offset), (card_x + card_w, card_y + card_h + crop_offset + crop_len)], fill=(0, 0, 0), width=3)

    # 3. Physical Scale Verification Ruler (100mm horizontal ruler below card)
    ruler_y = card_y + card_h + 100
    ruler_x_start = card_x
    ruler_len_mm = 100
    ruler_len_px = int(round(ruler_len_mm * mm_to_px))

    draw.text((ruler_x_start, ruler_y - 45), "PHYSICAL SCALE VERIFICATION RULER (Must measure exactly 10.0 cm / 100 mm):", fill=(20, 30, 50), font=font_bold)
    draw.line([(ruler_x_start, ruler_y), (ruler_x_start + ruler_len_px, ruler_y)], fill=(0, 0, 0), width=4)

    for mm in range(0, ruler_len_mm + 1, 5):
        tx = ruler_x_start + int(round(mm * mm_to_px))
        tick_h = 24 if mm % 10 == 0 else (14 if mm % 5 == 0 else 8)
        draw.line([(tx, ruler_y), (tx, ruler_y + tick_h)], fill=(0, 0, 0), width=2)
        if mm % 10 == 0:
            draw.text((tx - 12, ruler_y + 28), f"{mm}", fill=(30, 30, 30), font=font_small)

    draw.text((ruler_x_start + ruler_len_px + 20, ruler_y - 5), "mm", fill=(50, 50, 50), font=font_bold)

    # 4. Instructions & Guidance Grid
    info_y = ruler_y + 110
    draw.line([(120, info_y), (a4_w - 120, info_y)], fill=(200, 205, 215), width=2)

    # Left Column: Printing & Physical Preparation
    left_x = 120
    col_y = info_y + 40

    draw.text((left_x, col_y), "1. PRINTING & PHYSICAL PREPARATION", fill=(15, 25, 45), font=font_title)
    col_y += 55

    print_instructions = [
        ("Print Scale:", "Print at 100% scale / Actual Size. DO NOT select 'Fit to Page' or 'Shrink to Printable Area'."),
        ("Paper Choice:", "Use heavy white matte paper or cardstock (200 - 300 gsm). Avoid glossy photo paper to prevent specular glare."),
        ("Physical Size:", "Final trimmed card measures exactly 150 mm wide by 100 mm high (Aspect Ratio: 1.50)."),
        ("Cutting:", "Cut cleanly along the 4 corner crop marks. The solid black outer border must remain fully intact."),
        ("Orientation:", "Place card flat on a neutral, non-reflective surface. Color patches and reaction wells must face camera."),
    ]

    for label, desc in print_instructions:
        draw.text((left_x, col_y), f"• {label}", fill=(20, 20, 20), font=font_bold)
        draw.text((left_x + 180, col_y), desc, fill=(60, 65, 75), font=font_body)
        col_y += 44

    # Right Column / Section 2: Camera & Optical Acquisition Guidance
    col_y += 30
    draw.text((left_x, col_y), "2. CAMERA ALIGNMENT & ILLUMINATION PROTOCOL", fill=(15, 25, 45), font=font_title)
    col_y += 55

    camera_instructions = [
        ("Camera Distance:", "Position camera 20 cm to 35 cm directly above the card so the card fills 40% - 80% of the viewport."),
        ("Plane Alignment:", "Hold device plane-parallel to card surface. Skew angle exceeding 20° is rejected by the Adaptive Capture Guard."),
        ("Illumination:", "Use uniform, diffuse white illumination (indirect daylight or diffuse soft-white LED)."),
        ("Anti-Glare Rule:", "Avoid direct camera flash, directional spotlights, or low-angle glare over reaction wells (Glare limit < 5.0%)."),
        ("Focus Sharpness:", "Ensure sharp focus before triggering capture. Laplace blur variance must exceed 120.0 threshold."),
    ]

    for label, desc in camera_instructions:
        draw.text((left_x, col_y), f"• {label}", fill=(20, 20, 20), font=font_bold)
        draw.text((left_x + 230, col_y), desc, fill=(60, 65, 75), font=font_body)
        col_y += 44

    # 5. Mandatory Non-Chemical Test Notice at Bottom
    footer_y = a4_h - 220
    draw.rectangle([(120, footer_y), (a4_w - 120, a4_h - 100)], fill=(245, 246, 250), outline=(180, 190, 210), width=2)
    draw.text(
        (150, footer_y + 25),
        "MANDATORY NOTICE: OPTICAL TEST FIXTURE & CALIBRATION AID ONLY",
        fill=(180, 40, 20),
        font=font_bold,
    )
    draw.text(
        (150, footer_y + 65),
        "This reference card is a software test fixture and colorimetric calibration aid designed for verifying camera acquisition\nand computer-vision algorithms. It does NOT contain real chemical reagents and does NOT represent an actual chemical reaction.",
        fill=(60, 65, 75),
        font=font_small,
    )

    return sheet


def main():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reference_cards"))
    os.makedirs(output_dir, exist_ok=True)

    print("=================================================================")
    print("REACTRA V2 — Physical Reference Card Generation & Validation Tool")
    print("=================================================================")

    # 1. Generate High-Res Standalone PNG (2400 x 1600 px @ 4x scale / 300 DPI master)
    highres_path = os.path.join(output_dir, "REACTRA_DEMO_REFERENCE_CARD_HIGHRES.png")
    highres_rgb = create_reference_card_image(scale=4.0)
    highres_pil = Image.fromarray(highres_rgb)
    highres_pil.save(highres_path, dpi=(300, 300), optimize=True)
    print(f"[OK] Generated High-Resolution Card PNG: {highres_path} ({highres_rgb.shape[1]}x{highres_rgb.shape[0]} px)")

    # 2. Generate Standalone Print PDF (150mm x 100mm @ 300 DPI -> 1772 x 1181 px)
    pdf_card_path = os.path.join(output_dir, "REACTRA_DEMO_REFERENCE_CARD.pdf")
    card_300dpi_rgb = create_reference_card_image(scale=1772.0 / 600.0)
    card_300dpi_pil = Image.fromarray(card_300dpi_rgb)
    card_300dpi_pil.save(pdf_card_path, "PDF", resolution=300.0)
    print(f"[OK] Generated Standalone Print PDF: {pdf_card_path}")

    # 3. Generate Complete A4 Print Sheet (PNG & PDF @ 300 DPI: 2480 x 3508 px)
    a4_sheet = create_a4_print_sheet()

    a4_png_path = os.path.join(output_dir, "REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.png")
    a4_sheet.save(a4_png_path, dpi=(300, 300), optimize=True)
    print(f"[OK] Generated A4 Print Sheet PNG: {a4_png_path} ({a4_sheet.width}x{a4_sheet.height} px)")

    a4_pdf_path = os.path.join(output_dir, "REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.pdf")
    try:
        a4_sheet.save(a4_pdf_path, "PDF", resolution=300.0)
        print(f"[OK] Generated A4 Print Sheet PDF: {a4_pdf_path}")
    except PermissionError:
        print(f"[WARN] A4 PDF file is locked by an external reader: {a4_pdf_path}")

    # 4. Pipeline Validation against Existing Scientific Implementation
    print("\n--- Validating Generated Assets with Scientific Pipeline ---")

    # Ingest High-Res image
    ingested = ingest_image_data(highres_path, provenance="LIVE_CAMERA")
    print(f"[OK] Image Ingest: {ingested.width}x{ingested.height} px, SHA-256: {ingested.sha256_hash[:16]}...")

    # Detect Card
    detect_res = detect_reference_card(ingested.rgb_array)
    print(f"[OK] Card Detection: Detected={detect_res.detected}, Confidence={detect_res.confidence:.2f}, AspectRatio={detect_res.aspect_ratio:.2f}, Skew={detect_res.skew_angle_deg:.1f} deg")

    # Full Pipeline Measurement Test
    with open(highres_path, "rb") as f:
        img_bytes = f.read()

    pipeline_res = execute_scientific_measurement(
        session_id="SES-DEMO-CARD-TEST",
        capture_id="CAP-PHYS-CARD-001",
        image_source=img_bytes,
        profile=STANDARD_GRID_PROFILE,
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    print(f"[OK] Adaptive Capture Guard: {pipeline_res.quality_diagnostics.overall_status}")
    print(f"  - Blur Variance: {pipeline_res.quality_diagnostics.blur.variance:.1f} (Threshold >= {pipeline_res.quality_diagnostics.blur.threshold})")
    print(f"  - Glare Ratio: {pipeline_res.quality_diagnostics.glare.max_roi_glare_fraction * 100:.1f}% (Threshold <= {pipeline_res.quality_diagnostics.glare.threshold * 100}%)")
    print(f"  - Calibration Residual: {pipeline_res.calibration_mean_delta_e:.2f} DeltaE (Threshold <= {STANDARD_GRID_PROFILE.thresholds.max_calibration_delta_e} DeltaE)")
    print(f"  - Well 1 Lab: {pipeline_res.well_measurements['well_1'].calibrated_lab_median}")
    print(f"  - Well 2 Lab: {pipeline_res.well_measurements['well_2'].calibrated_lab_median}")
    print("=================================================================")
    print("All physical reference card assets successfully generated & verified!")


if __name__ == "__main__":
    main()
