"""REACTRA V2 — Unit Tests for Scientific Modules and Pipeline.

Tests image I/O, card detection, perspective warp, blur, exposure, glare,
color conversion, calibration, ROI extraction, robust estimation, and kinetic timing.
"""

import base64
import cv2
import numpy as np
import pytest

from app.scientific.image_io import ingest_image_data, ImageValidationError
from app.scientific.card_detection import detect_reference_card, order_corners
from app.scientific.perspective import normalize_card_perspective
from app.scientific.blur import evaluate_blur
from app.scientific.exposure import evaluate_exposure
from app.scientific.glare import detect_specular_glare
from app.scientific.color import rgb_to_lab, delta_e_76
from app.scientific.calibration import calibrate_reference_card
from app.scientific.roi import extract_reaction_rois
from app.scientific.robust_estimation import robust_estimate_well_color
from app.scientific.timing_gate import evaluate_reaction_timing
from app.scientific.measurement import execute_scientific_measurement, MeasurementQualityError
from app.scientific.profiles import STANDARD_GRID_PROFILE
from tests.fixtures.synthetic_cards import (
    generate_valid_card,
    generate_blurred_card,
    generate_glare_card,
    generate_underexposed_card,
    generate_overexposed_card,
    generate_missing_card,
)


def _card_to_base64(img_arr: np.ndarray) -> str:
    """Encode OpenCV RGB array to base64 JPEG data URL for testing."""
    bgr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".png", bgr)
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def test_image_ingest_and_validation():
    """Verify format, channels, and provenance validation."""
    valid_card = generate_valid_card()
    b64 = _card_to_base64(valid_card)

    # Valid canonical LIVE_CAMERA ingest
    ingested = ingest_image_data(b64, provenance="LIVE_CAMERA")
    assert ingested.width == 600
    assert ingested.height == 400
    assert ingested.channels == 3
    assert ingested.provenance == "LIVE_CAMERA"
    assert len(ingested.sha256_hash) == 64

    # Backwards-compatible alias DIRECT_CAMERA normalizes to LIVE_CAMERA
    ingested_alias = ingest_image_data(b64, provenance="DIRECT_CAMERA")
    assert ingested_alias.provenance == "LIVE_CAMERA"

    # Valid IMPORTED_IMAGE ingest
    ingested_imported = ingest_image_data(b64, provenance="IMPORTED_IMAGE")
    assert ingested_imported.provenance == "IMPORTED_IMAGE"

    # Invalid provenance rejection
    with pytest.raises(ImageValidationError, match="Invalid provenance"):
        ingest_image_data(b64, provenance="UNVERIFIED_SOURCE")

    # Invalid small dimensions
    tiny = np.zeros((100, 100, 3), dtype=np.uint8)
    tiny_b64 = _card_to_base64(tiny)
    with pytest.raises(ImageValidationError, match="below required minimum"):
        ingest_image_data(tiny_b64, provenance="LIVE_CAMERA")


def test_card_detection_and_ordering():
    """Verify reference card quadrilateral detection and corner ordering."""
    card = generate_valid_card()
    res = detect_reference_card(card, target_aspect_ratio=1.5)
    
    assert res.detected is True
    assert res.corners is not None
    assert res.corners.shape == (4, 2)
    assert res.confidence > 0.7
    assert abs(res.aspect_ratio - 1.5) < 0.2


def test_perspective_normalization():
    """Verify 4-point homography transform to canonical dimensions."""
    card = generate_valid_card()
    corners = np.array([[0, 0], [599, 0], [599, 399], [0, 399]], dtype=np.float32)
    
    warp_res = normalize_card_perspective(card, corners, canonical_width=600, canonical_height=400)
    assert warp_res.warped_rgb.shape == (400, 600, 3)
    assert warp_res.canonical_width == 600
    assert warp_res.canonical_height == 400


def test_blur_metric_evaluation():
    """Verify Laplacian blur variance distinguishes sharp vs blurred images."""
    sharp_card = generate_valid_card()
    blurred_card = generate_blurred_card()

    sharp_res = evaluate_blur(sharp_card, min_variance_threshold=100.0)
    assert sharp_res.passed is True
    assert sharp_res.variance > 100.0

    blurred_res = evaluate_blur(blurred_card, min_variance_threshold=100.0)
    assert blurred_res.passed is False
    assert blurred_res.variance < 50.0


def test_exposure_metric_evaluation():
    """Verify exposure evaluation flags underexposure and overexposure."""
    valid_card = generate_valid_card()
    under_card = generate_underexposed_card()
    over_card = generate_overexposed_card()

    valid_res = evaluate_exposure(valid_card)
    assert valid_res.passed is True

    under_res = evaluate_exposure(under_card)
    assert under_res.passed is False
    assert "underexposed" in under_res.explanation.lower()

    over_res = evaluate_exposure(over_card)
    assert over_res.passed is False
    assert "overexposed" in over_res.explanation.lower()


def test_specular_glare_detection():
    """Verify specular reflection detection on reaction wells."""
    valid_card = generate_valid_card()
    glare_card = generate_glare_card()
    rois = [("well_1", (80, 180, 120, 120))]

    valid_glare = detect_specular_glare(valid_card, rois, max_glare_fraction=0.05)
    assert valid_glare.passed is True
    assert valid_glare.max_roi_glare_fraction < 0.05

    bad_glare = detect_specular_glare(glare_card, rois, max_glare_fraction=0.05)
    assert bad_glare.passed is False
    assert bad_glare.max_roi_glare_fraction > 0.10


def test_color_and_calibration():
    """Verify CIE L*a*b* conversion and affine calibration residual."""
    card = generate_valid_card()
    calib = calibrate_reference_card(card, STANDARD_GRID_PROFILE.calibration_patches, max_delta_e_threshold=18.0)
    
    assert calib.passed is True
    assert calib.mean_delta_e < 15.0
    assert calib.affine_matrix.shape == (3, 4)
    assert len(calib.patch_diagnostics) == 6


def test_roi_and_robust_estimation():
    """Verify ROI extraction, spatial erosion, and robust color median estimation."""
    card = generate_valid_card(reaction_rgb=(140, 20, 140))
    rois = extract_reaction_rois(card, STANDARD_GRID_PROFILE.reaction_rois)
    assert len(rois) == 2

    glare_mask = np.zeros((400, 600), dtype=np.uint8)
    well_meas = robust_estimate_well_color(rois[0], glare_mask=glare_mask, min_valid_pixels=50)
    
    assert well_meas.is_valid is True
    assert well_meas.valid_pixel_count > 50
    assert well_meas.glare_pixel_count == 0
    # Purple reaction well has positive a* and negative/neutral b*
    L, a, b = well_meas.calibrated_lab_median
    assert L > 20.0
    assert a > 20.0  # Purple/magenta chroma


def test_timing_gate():
    """Verify reaction timing window compliance checking."""
    # Compliant 30s elapsed
    t_ok = evaluate_reaction_timing(30.0, target_window_seconds=30, min_window_seconds=10, max_window_seconds=120)
    assert t_ok.passed is True
    assert t_ok.compliance_status == "IN_WINDOW"

    # Too early (5s)
    t_early = evaluate_reaction_timing(5.0, target_window_seconds=30, min_window_seconds=10, max_window_seconds=120)
    assert t_early.passed is False
    assert t_early.compliance_status == "EARLY"

    # Expired (150s)
    t_exp = evaluate_reaction_timing(150.0, target_window_seconds=30, min_window_seconds=10, max_window_seconds=120)
    assert t_exp.passed is False
    assert t_exp.compliance_status == "EXPIRED"


def test_full_scientific_pipeline_valid_card():
    """Execute complete end-to-end scientific pipeline on valid card fixture."""
    card = generate_valid_card()
    b64 = _card_to_base64(card)

    meas = execute_scientific_measurement(
        image_source=b64,
        session_id="SES-TEST-001",
        capture_id="CAP-TEST-001",
        provenance="LIVE_CAMERA",
        profile=STANDARD_GRID_PROFILE,
        elapsed_seconds=30.0,
    )

    assert meas.session_id == "SES-TEST-001"
    assert meas.capture_id == "CAP-TEST-001"
    assert meas.provenance == "LIVE_CAMERA"
    assert meas.calibration_passed is True
    assert "well_1" in meas.well_measurements
    assert meas.quality_diagnostics.overall_status == "READY"
    assert meas.quality_diagnostics.passed_all_hard_gates is True


def test_pipeline_determinism_and_reproducibility():
    """Verify pipeline produces identical numeric results for the same input."""
    card = generate_valid_card()
    b64 = _card_to_base64(card)

    meas1 = execute_scientific_measurement(
        image_source=b64,
        session_id="SES-DET-001",
        capture_id="CAP-001",
        profile=STANDARD_GRID_PROFILE,
        elapsed_seconds=30.0,
    )
    meas2 = execute_scientific_measurement(
        image_source=b64,
        session_id="SES-DET-001",
        capture_id="CAP-002",
        profile=STANDARD_GRID_PROFILE,
        elapsed_seconds=30.0,
    )

    w1_m1 = meas1.well_measurements["well_1"].calibrated_lab_median
    w1_m2 = meas2.well_measurements["well_1"].calibrated_lab_median
    assert np.allclose(w1_m1, w1_m2, atol=1e-5)
    assert abs(meas1.calibration_mean_delta_e - meas2.calibration_mean_delta_e) < 1e-5
