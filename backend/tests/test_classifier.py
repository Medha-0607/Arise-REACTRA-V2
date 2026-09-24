"""REACTRA V2 — Presumptive Classifier Unit and Integration Test Suite.

Verifies:
1. Decision boundaries: Positive, Negative, Inconclusive
2. Scientific invariants: Quality, Calibration, Timing, Versioning
3. Rejection of unknown profiles or version mismatches
4. Full API endpoint integration: POST /api/v1/sessions/{id}/classify
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.domain.state_machine import SessionState, OutcomeState
from app.scientific.profiles import (
    STANDARD_GRID_PROFILE,
    ScientificAssayProfile,
    ClassifierConfig,
)
from app.scientific.measurement import (
    ValidatedMeasurement,
    WellColorMeasurement,
)
from app.scientific.quality import QualityDiagnostics
from app.scientific.blur import BlurMetricResult
from app.scientific.exposure import ExposureMetricResult
from app.scientific.glare import GlareMetricResult
from app.scientific.card_detection import CardDetectionResult
from app.scientific.calibration import CalibrationResult
from app.scientific.timing_gate import TimingGateResult
from app.scientific.classifier import (
    classify_measurement,
    ClassificationPreconditionError,
)
from app.services.classification_service import (
    ClassificationService,
    register_validated_measurement,
)


import numpy as np


def _make_dummy_diagnostics(passed: bool = True, timing_status: str = "VALID") -> QualityDiagnostics:
    return QualityDiagnostics(
        overall_status="READY" if passed else "RECAPTURE",
        passed_all_hard_gates=passed,
        blur=BlurMetricResult(variance=450.0 if passed else 50.0, threshold=120.0, passed=passed, explanation=""),
        exposure=ExposureMetricResult(mean_luminance=120.0, underexposed_fraction=0.0, overexposed_fraction=0.0, dynamic_range=200, passed=passed, explanation=""),
        glare=GlareMetricResult(glare_mask=np.zeros((10, 10), dtype=np.uint8), max_roi_glare_fraction=0.01 if passed else 0.20, threshold=0.05, passed=passed, explanation="", roi_glare_fractions={}),
        card_detection=CardDetectionResult(detected=True, corners=None, confidence=0.95, aspect_ratio=1.5, skew_angle_deg=2.0, area_fraction=0.4, reason=""),
        alignment_passed=passed,
        skew_angle_deg=2.0,
        calibration=CalibrationResult(passed=passed, mean_delta_e=4.0 if passed else 25.0, threshold=18.0, affine_matrix=np.eye(3, 4), patch_diagnostics={}, explanation=""),
        timing=TimingGateResult(compliance_status=timing_status, elapsed_seconds=30.0, target_window_seconds=30, min_window_seconds=10, max_window_seconds=120, passed=(timing_status != "INVALID"), explanation=""),
        failure_reasons=[] if passed else ["Optical quality failed"],
    )


def _make_dummy_measurement(
    profile_id: str = "marquis-standard-v1",
    profile_version: str = "1.0.0",
    algorithm_version: str = "2.0.0",
    calibrated_well_lab=(35.0, 30.0, -15.0),
    calibration_passed: bool = True,
    passed_quality: bool = True,
    timing_compliance: str = "VALID",
) -> ValidatedMeasurement:
    return ValidatedMeasurement(
        measurement_id="MEA-TEST-100",
        session_id="SES-TEST-100",
        capture_id="CAP-TEST-100",
        profile_id=profile_id,
        profile_version=profile_version,
        algorithm_version=algorithm_version,
        reference_card_version="ref-card-grid-3x2",
        provenance="LIVE_CAMERA",
        measured_at=datetime.now(timezone.utc).isoformat(),
        timing_compliance=timing_compliance,
        elapsed_seconds=30.0,
        calibration_mean_delta_e=4.0 if calibration_passed else 25.0,
        calibration_passed=calibration_passed,
        well_measurements={
            "well_1": WellColorMeasurement(
                roi_id="well_1",
                name="Primary Reaction Well",
                bbox=(80, 180, 120, 120),
                sampled_bbox=(88, 188, 104, 104),
                valid_pixel_count=120,
                glare_pixel_count=0,
                raw_lab_median=calibrated_well_lab,
                calibrated_lab_median=calibrated_well_lab,
                calibrated_lab_trimmed_mean=calibrated_well_lab,
                lab_std_dev=(1.0, 1.0, 1.0),
                is_valid=True,
            ),
            "well_2": WellColorMeasurement(
                roi_id="well_2",
                name="Negative Control Well",
                bbox=(400, 180, 120, 120),
                sampled_bbox=(408, 188, 104, 104),
                valid_pixel_count=120,
                glare_pixel_count=0,
                raw_lab_median=(90.0, 0.0, 2.0),
                calibrated_lab_median=(90.0, 0.0, 2.0),
                calibrated_lab_trimmed_mean=(90.0, 0.0, 2.0),
                lab_std_dev=(1.0, 1.0, 1.0),
                is_valid=True,
            ),
        },
        quality_diagnostics=_make_dummy_diagnostics(passed=passed_quality, timing_status=timing_compliance),
    )


def test_classifier_positive_outcome():
    """Verify presumptive positive when measured Lab is close to nominal positive centroid."""
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 28.0, -14.0))  # Distance < 5.0
    res = classify_measurement(meas, STANDARD_GRID_PROFILE)
    assert res.outcome == OutcomeState.PRESUMPTIVE_POSITIVE
    assert res.class_distance_1 <= STANDARD_GRID_PROFILE.classifier_config.positive_distance_threshold
    assert res.explanation.decision_margin > 0


def test_classifier_negative_outcome():
    """Verify presumptive negative when measured Lab is far from positive centroid (near negative blank)."""
    meas = _make_dummy_measurement(calibrated_well_lab=(90.0, 0.0, 2.0))  # Distance ~ 65.0
    res = classify_measurement(meas, STANDARD_GRID_PROFILE)
    assert res.outcome == OutcomeState.PRESUMPTIVE_NEGATIVE
    assert res.class_distance_1 >= STANDARD_GRID_PROFILE.classifier_config.negative_distance_threshold


def test_classifier_inconclusive_zone():
    """Verify inconclusive when measured Lab falls between positive (25.0) and negative (45.0) thresholds."""
    # Distance to (35, 30, -15) is ~ 35.0
    meas = _make_dummy_measurement(calibrated_well_lab=(60.0, 10.0, 0.0))
    res = classify_measurement(meas, STANDARD_GRID_PROFILE)
    assert res.outcome == OutcomeState.INCONCLUSIVE
    assert 25.0 < res.class_distance_1 < 45.0


def test_classifier_rejects_failed_quality_gates():
    """Verify invariant: Classifier refuses to run on failed quality diagnostics."""
    meas = _make_dummy_measurement(passed_quality=False)
    with pytest.raises(ClassificationPreconditionError, match="Adaptive Capture Guard"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_rejects_failed_calibration():
    """Verify invariant: Classifier refuses to run when color calibration failed."""
    meas = _make_dummy_measurement(calibration_passed=False)
    with pytest.raises(ClassificationPreconditionError, match="color calibration failed"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_rejects_invalid_timing():
    """Verify invariant: Classifier refuses to run when reaction incubation timing was invalid."""
    meas = _make_dummy_measurement(timing_compliance="INVALID")
    with pytest.raises(ClassificationPreconditionError, match="timing gate failed"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_rejects_profile_mismatch():
    """Verify invariant: Classifier rejects measurement bound to a different profile ID."""
    meas = _make_dummy_measurement(profile_id="scott-cocaine-v1")
    with pytest.raises(ClassificationPreconditionError, match="Profile mismatch"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_rejects_profile_version_mismatch():
    """Verify invariant: Classifier rejects measurement bound to a different profile version."""
    meas = _make_dummy_measurement(profile_version="2.0.0")
    with pytest.raises(ClassificationPreconditionError, match="Profile version mismatch"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_rejects_algorithm_version_mismatch():
    """Verify invariant: Classifier rejects measurement with incompatible algorithm version."""
    meas = _make_dummy_measurement(algorithm_version="1.0.0")
    with pytest.raises(ClassificationPreconditionError, match="Algorithm version incompatibility"):
        classify_measurement(meas, STANDARD_GRID_PROFILE)


def test_classifier_deterministic_output():
    """Verify determinism: Identical measurement and profile produce bit-exact decisions."""
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    res1 = classify_measurement(meas, STANDARD_GRID_PROFILE)
    res2 = classify_measurement(meas, STANDARD_GRID_PROFILE)
    assert res1.outcome == res2.outcome
    assert res1.class_distance_1 == res2.class_distance_1
    assert res1.decision_margin == res2.decision_margin
    assert res1.explanation.model_dump() == res2.explanation.model_dump()


def test_classification_api_integration(db_session: Session):
    """End-to-end integration test: create session -> transition to READY_FOR_CLASSIFICATION -> classify."""
    client = TestClient(app)

    # 1. Create session
    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-CLASS-001",
            "operator_id": "OFC-CLASS-99",
            "device_enrollment_id": "DEV-CLASS-01",
            "assay_profile_id": "marquis-standard-v1",
            "capture_mode": "LIVE_CAMERA",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # 2. Transition through workflow to READY_FOR_CLASSIFICATION
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )

    # Register measurement for this session
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)

    # 3. Call Classify endpoint
    classify_res = client.post(f"/api/v1/sessions/{session_id}/classify")
    assert classify_res.status_code == 200
    data = classify_res.json()
    assert data["session_id"] == session_id
    assert data["outcome"] == "PRESUMPTIVE_POSITIVE"
    assert data["session_status"] == "CLASSIFIED"
    assert "explanation" in data
    assert data["explanation"]["presumptive_disclaimer"] is not None

    # 4. Verify session state updated in DB
    get_res = client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.json()["status"] == "CLASSIFIED"


def test_classification_rejects_unknown_profile(db_session: Session):
    """Verify invariant: Classifier rejects unknown or unregistered assay profiles."""
    from app.services.classification_service import ClassificationPreconditionError
    svc = ClassificationService(db_session)
    
    client = TestClient(app)
    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-UNKNOWN-001",
            "operator_id": "OFC-001",
            "device_enrollment_id": "DEV-CLASS-01",
            "assay_profile_id": "unknown-nonexistent-profile",
            "capture_mode": "LIVE_CAMERA",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # Transition to READY_FOR_CLASSIFICATION
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )

    # Register valid measurement with unknown profile ID
    meas = _make_dummy_measurement(profile_id="unknown-nonexistent-profile")
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)

    with pytest.raises(ClassificationPreconditionError, match="Unknown assay profile"):
        svc.classify_session(session_id)

