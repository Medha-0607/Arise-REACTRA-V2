"""REACTRA V2 — Integration Tests for Measurement Service & Quality Gating.

Verifies end-to-end database persistence, quality gate enforcement,
audit logging, state machine synchronization, and classifier decoupling.
"""

import base64
import cv2
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.services.session_service import SessionService
from app.services.measurement_service import MeasurementService
from app.schemas.session import SessionCreateRequest
from app.domain.state_machine import CaptureSource
from tests.fixtures.synthetic_cards import (
    generate_valid_card,
    generate_blurred_card,
    generate_glare_card,
    generate_underexposed_card,
    generate_missing_card,
)


def _card_to_base64(img_arr: np.ndarray) -> str:
    bgr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".png", bgr)
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def test_measurement_service_success_lifecycle(db_session: Session):
    """Test successful measurement execution transitioning session to READY_FOR_CLASSIFICATION."""
    session_service = SessionService(db_session)
    meas_service = MeasurementService(db_session)

    # 1. Create session in DRAFT
    req = SessionCreateRequest(
        case_id="CAS-MEAS-001",
        operator_id="OFC-8801",
        device_enrollment_id="DEV-MEAS-01",
        assay_profile_id="marquis-standard-v1",
        assay_profile_version="v1.0.0",
        capture_mode=CaptureSource.LIVE_CAMERA,
    )
    session = session_service.create_session(req)
    assert session.status == "DRAFT"

    # 2. Execute measurement with valid synthetic card
    valid_card = generate_valid_card()
    b64 = _card_to_base64(valid_card)

    outcome = meas_service.process_capture_and_measure(
        session_id=session.id,
        image_source=b64,
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    assert outcome.passed_quality_gates is True
    assert outcome.session_status == "READY_FOR_CLASSIFICATION"
    assert outcome.overall_quality_status == "READY"
    assert outcome.validated_measurement is not None
    assert outcome.validated_measurement.calibration_passed is True

    # 3. Verify session in DB updated to READY_FOR_CLASSIFICATION
    db_session.refresh(session)
    assert session.status == "READY_FOR_CLASSIFICATION"
    assert session.measurement is not None
    assert session.measurement.quality_status == "READY"
    assert session.measurement.reaction_lab_l is not None

    # 4. Verify audit events persisted
    timeline = session_service.get_timeline(session.id)
    event_types = [e.event_type for e in timeline]
    assert "SESSION_CREATED" in event_types
    assert "CAPTURE_INITIATED" in event_types
    assert "MEASUREMENT_VALIDATED" in event_types


def test_measurement_service_rejection_blurred_card(db_session: Session):
    """Test that blur failure transitions session to VALIDATION_FAILED and blocks ValidatedMeasurement."""
    session_service = SessionService(db_session)
    meas_service = MeasurementService(db_session)

    session = session_service.create_session(
        SessionCreateRequest(
            case_id="CAS-BLUR-001",
            operator_id="OFC-8802",
            device_enrollment_id="DEV-MEAS-01",
            assay_profile_id="marquis-standard-v1",
        )
    )

    blurred_b64 = _card_to_base64(generate_blurred_card())
    outcome = meas_service.process_capture_and_measure(
        session_id=session.id,
        image_source=blurred_b64,
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    assert outcome.passed_quality_gates is False
    assert outcome.session_status == "VALIDATION_FAILED"
    assert outcome.overall_quality_status == "RECAPTURE"
    assert outcome.validated_measurement is None
    assert any("blur" in r.lower() for r in outcome.quality_diagnostics.failure_reasons)

    # Verify session DB status
    db_session.refresh(session)
    assert session.status == "VALIDATION_FAILED"
    assert session.measurement.quality_status == "RECAPTURE"


def test_measurement_service_rejection_glare_card(db_session: Session):
    """Test that severe specular glare in reaction well triggers VALIDATION_FAILED."""
    session_service = SessionService(db_session)
    meas_service = MeasurementService(db_session)

    session = session_service.create_session(
        SessionCreateRequest(
            case_id="CAS-GLARE-001",
            operator_id="OFC-8803",
            device_enrollment_id="DEV-MEAS-01",
            assay_profile_id="marquis-standard-v1",
        )
    )

    glare_b64 = _card_to_base64(generate_glare_card())
    outcome = meas_service.process_capture_and_measure(
        session_id=session.id,
        image_source=glare_b64,
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    assert outcome.passed_quality_gates is False
    assert outcome.session_status == "VALIDATION_FAILED"
    assert outcome.overall_quality_status == "RECAPTURE"
    assert outcome.validated_measurement is None
    assert any("glare" in r.lower() for r in outcome.quality_diagnostics.failure_reasons)


def test_measurement_service_rejection_missing_card(db_session: Session):
    """Test that card localization failure triggers VALIDATION_FAILED."""
    session_service = SessionService(db_session)
    meas_service = MeasurementService(db_session)

    session = session_service.create_session(
        SessionCreateRequest(
            case_id="CAS-MISS-001",
            operator_id="OFC-8804",
            device_enrollment_id="DEV-MEAS-01",
            assay_profile_id="marquis-standard-v1",
        )
    )

    missing_b64 = _card_to_base64(generate_missing_card())
    outcome = meas_service.process_capture_and_measure(
        session_id=session.id,
        image_source=missing_b64,
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    assert outcome.passed_quality_gates is False
    assert outcome.session_status == "VALIDATION_FAILED"
    assert outcome.validated_measurement is None


def test_classifier_decoupling_invariant(db_session: Session):
    """Critical Invariant: ValidatedMeasurement must provide all data needed by classifier with ZERO raw image data."""
    session_service = SessionService(db_session)
    meas_service = MeasurementService(db_session)

    session = session_service.create_session(
        SessionCreateRequest(
            case_id="CAS-DECOUPLE-001",
            operator_id="OFC-8805",
            device_enrollment_id="DEV-MEAS-01",
            assay_profile_id="marquis-standard-v1",
        )
    )
    outcome = meas_service.process_capture_and_measure(
        session_id=session.id,
        image_source=_card_to_base64(generate_valid_card()),
        provenance="LIVE_CAMERA",
        elapsed_seconds=30.0,
    )

    meas = outcome.validated_measurement
    assert meas is not None

    # The future classifier only requires:
    # 1. Profile binding
    assert meas.profile_id == "marquis-standard-v1"
    # 2. Timing status
    assert meas.timing_compliance == "IN_WINDOW"
    # 3. Calibration metrics
    assert meas.calibration_passed is True
    assert meas.calibration_mean_delta_e > 0.0
    # 4. Calibrated reaction well L*a*b* coordinates
    well_1 = meas.well_measurements["well_1"]
    assert len(well_1.calibrated_lab_median) == 3
    assert len(well_1.calibrated_lab_trimmed_mean) == 3
    assert len(well_1.lab_std_dev) == 3
    assert well_1.valid_pixel_count >= 50
    # 5. Provenance
    assert meas.provenance in ("LIVE_CAMERA", "DIRECT_CAMERA")


@pytest.mark.asyncio
async def test_measure_api_endpoint(async_client: AsyncClient):
    """Test POST /api/v1/sessions/{session_id}/measure HTTP route."""
    # Create session
    create_res = await async_client.post("/api/v1/sessions", json={
        "case_id": "CAS-API-MEAS-01",
        "operator_id": "OFC-8806",
        "device_enrollment_id": "DEV-MEAS-01",
        "assay_profile_id": "marquis-standard-v1",
        "assay_profile_version": "v1.0.0",
        "capture_mode": "LIVE_CAMERA",
    })
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    # Call measure endpoint with valid card
    measure_res = await async_client.post(f"/api/v1/sessions/{sess_id}/measure", json={
        "image_base64": _card_to_base64(generate_valid_card()),
        "provenance": "LIVE_CAMERA",
        "elapsed_seconds": 30.0,
    })
    assert measure_res.status_code == 200
    data = measure_res.json()
    assert data["passed_quality_gates"] is True
    assert data["session_status"] == "READY_FOR_CLASSIFICATION"
    assert data["validated_measurement"]["well_measurements"]["well_1"]["calibrated_lab_median"] is not None


@pytest.mark.asyncio
async def test_measure_api_recapture_from_ready_for_classification(async_client: AsyncClient):
    """Test that a session already in READY_FOR_CLASSIFICATION can be recaptured/remeasured cleanly."""
    create_res = await async_client.post("/api/v1/sessions", json={
        "case_id": "CAS-API-RECAP-01",
        "operator_id": "OFC-8806",
        "device_enrollment_id": "DEV-MEAS-01",
        "assay_profile_id": "marquis-standard-v1",
        "assay_profile_version": "v1.0.0",
        "capture_mode": "LIVE_CAMERA",
    })
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    # Initial measurement -> READY_FOR_CLASSIFICATION
    res1 = await async_client.post(f"/api/v1/sessions/{sess_id}/measure", json={
        "image_base64": _card_to_base64(generate_valid_card()),
        "provenance": "LIVE_CAMERA",
        "elapsed_seconds": 30.0,
    })
    assert res1.status_code == 200
    assert res1.json()["session_status"] == "READY_FOR_CLASSIFICATION"

    # Second measurement (Recapture) -> Must NOT throw 500 or InvalidTransitionError
    res2 = await async_client.post(f"/api/v1/sessions/{sess_id}/measure", json={
        "image_base64": _card_to_base64(generate_valid_card()),
        "provenance": "LIVE_CAMERA",
        "elapsed_seconds": 32.0,
    })
    assert res2.status_code == 200
    assert res2.json()["session_status"] == "READY_FOR_CLASSIFICATION"
    assert res2.json()["passed_quality_gates"] is True


@pytest.mark.asyncio
async def test_measure_api_missing_card_structured_rejection_no_500(async_client: AsyncClient):
    """Test that a 16:9 screenshot / image with no reference card produces structured rejection, NOT HTTP 500."""
    create_res = await async_client.post("/api/v1/sessions", json={
        "case_id": "CAS-API-NOCARD-01",
        "operator_id": "OFC-8806",
        "device_enrollment_id": "DEV-MEAS-01",
        "assay_profile_id": "marquis-standard-v1",
        "assay_profile_version": "v1.0.0",
        "capture_mode": "LIVE_CAMERA",
    })
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    # Create a blank 16:9 image (1280x720) with no reference card
    blank_16_9 = np.full((720, 1280, 3), (120, 120, 120), dtype=np.uint8)
    _, buf = cv2.imencode(".png", blank_16_9)
    b64_str = f"data:image/png;base64,{base64.b64encode(buf).decode('ascii')}"

    measure_res = await async_client.post(f"/api/v1/sessions/{sess_id}/measure", json={
        "image_base64": b64_str,
        "provenance": "LIVE_CAMERA",
        "elapsed_seconds": 30.0,
    })

    # Must return structured 200 with passed_quality_gates=False (NOT HTTP 500)
    assert measure_res.status_code == 200
    data = measure_res.json()
    assert data["passed_quality_gates"] is False
    assert data["session_status"] == "VALIDATION_FAILED"
    assert data["validated_measurement"] is None
    assert data["quality_diagnostics"]["checks"]["card_detection"]["detected"] is False
    assert round(data["quality_diagnostics"]["checks"]["card_detection"]["aspect_ratio"], 2) == 1.78


@pytest.mark.asyncio
async def test_measure_api_imported_image_physical_card(async_client: AsyncClient):
    """Test that the high-resolution reference card loaded as IMPORTED_IMAGE succeeds completely."""
    import os
    ref_card_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "reference_cards", "REACTRA_DEMO_REFERENCE_CARD_HIGHRES.png")
    )
    if not os.path.exists(ref_card_path):
        pytest.skip("High-resolution reference card not yet generated on filesystem.")

    with open(ref_card_path, "rb") as f:
        card_bytes = f.read()
    b64_str = f"data:image/png;base64,{base64.b64encode(card_bytes).decode('ascii')}"

    create_res = await async_client.post("/api/v1/sessions", json={
        "case_id": "CAS-API-IMPORT-01",
        "operator_id": "OFC-8806",
        "device_enrollment_id": "DEV-MEAS-01",
        "assay_profile_id": "marquis-standard-v1",
        "assay_profile_version": "v1.0.0",
        "capture_mode": "IMPORTED_IMAGE",
    })
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    measure_res = await async_client.post(f"/api/v1/sessions/{sess_id}/measure", json={
        "image_base64": b64_str,
        "provenance": "IMPORTED_IMAGE",
        "elapsed_seconds": 30.0,
    })
    assert measure_res.status_code == 200
    data = measure_res.json()
    assert data["passed_quality_gates"] is True
    assert data["session_status"] == "READY_FOR_CLASSIFICATION"
    assert data["validated_measurement"]["provenance"] == "IMPORTED_IMAGE"
    assert data["quality_diagnostics"]["checks"]["card_detection"]["detected"] is True
    assert data["quality_diagnostics"]["checks"]["calibration"]["passed"] is True

