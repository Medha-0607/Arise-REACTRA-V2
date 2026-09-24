"""
Integration tests for Session Lifecycle, Persistence, and API Endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_create_and_retrieve(async_client: AsyncClient):
    """Verifies that creating a session returns 201 Created and initializes all child shells."""
    payload = {
        "case_id": "CAS-2026-TEST-001",
        "event_id": "EVT-TEST-1",
        "operator_id": "OFC-TEST-99",
        "device_enrollment_id": "DEV-FIELD-01",
        "field_officer_name": "Test Officer",
        "assay_profile_id": "marquis-standard-v1",
        "assay_profile_version": "v1.0.0",
        "capture_mode": "LIVE_CAMERA",
        "gps_status": "OPERATOR_DECLARED",
        "location_description": "Test Checkpoint",
        "officer_notes": "Initial test setup notes",
    }

    create_resp = await async_client.post("/api/v1/sessions", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.json()
    
    session_id = data["id"]
    assert session_id.startswith("SES-")
    assert data["status"] == "DRAFT"
    assert data["case_id"] == "CAS-2026-TEST-001"
    assert data["operator_id"] == "OFC-TEST-99"
    assert data["assay_profile_id"] == "marquis-standard-v1"
    assert data["timing"] is not None
    assert data["measurement"] is not None
    assert data["procedural_context"] is not None
    assert len(data["audit_events"]) >= 1
    assert data["audit_events"][0]["event_type"] == "SESSION_CREATED"

    # Retrieve session by ID
    get_resp = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == session_id


@pytest.mark.asyncio
async def test_session_valid_lifecycle_transitions(async_client: AsyncClient):
    """Verifies full valid lifecycle progression from DRAFT to COMPLETED."""
    # 1. Create
    payload = {
        "case_id": "CAS-LIFECYCLE-001",
        "operator_id": "OFC-88",
        "device_enrollment_id": "DEV-FIELD-01",
        "assay_profile_id": "marquis-standard-v1",
    }
    create_resp = await async_client.post("/api/v1/sessions", json=payload)
    session_id = create_resp.json()["id"]

    # 2. DRAFT -> CAPTURED
    resp1 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "CAPTURED", "actor_id": "OFC-88"},
    )
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "CAPTURED"

    # 3. CAPTURED -> QUALITY_CHECKING
    resp2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "QUALITY_CHECKING", "actor_id": "Local Guard"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "QUALITY_CHECKING"

    # 4. QUALITY_CHECKING -> READY_FOR_CLASSIFICATION (with quality_passed=True)
    resp3 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "READY_FOR_CLASSIFICATION"
    assert resp3.json()["measurement"]["quality_status"] == "PASS"

    # 5. READY_FOR_CLASSIFICATION -> CLASSIFIED
    resp4 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "CLASSIFIED", "actor_id": "Classifier Engine"},
    )
    assert resp4.status_code == 200
    assert resp4.json()["status"] == "CLASSIFIED"

    # 6. CLASSIFIED -> EVIDENCE_SEALED
    resp5 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "EVIDENCE_SEALED", "actor_id": "Crypto Module"},
    )
    assert resp5.status_code == 200
    assert resp5.json()["status"] == "EVIDENCE_SEALED"

    # 7. EVIDENCE_SEALED -> COMPLETED
    resp6 = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "COMPLETED", "actor_id": "OFC-88"},
    )
    assert resp6.status_code == 200
    assert resp6.json()["status"] == "COMPLETED"

    # Check Timeline Events
    timeline_resp = await async_client.get(f"/api/v1/sessions/{session_id}/timeline")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert timeline["session_id"] == session_id
    assert timeline["current_status"] == "COMPLETED"
    # Should have 1 creation event + 6 transition events = 7 events
    assert len(timeline["events"]) == 7


@pytest.mark.asyncio
async def test_session_invalid_transition_rejected(async_client: AsyncClient):
    """Verifies that an illegal transition is rejected with 400 Bad Request."""
    create_resp = await async_client.post(
        "/api/v1/sessions",
        json={"case_id": "CAS-INVALID-001", "operator_id": "OFC-12", "device_enrollment_id": "DEV-FIELD-01"},
    )
    session_id = create_resp.json()["id"]

    # Try illegal jump: DRAFT -> CLASSIFIED
    bad_resp = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "CLASSIFIED"},
    )
    assert bad_resp.status_code == 400
    error_data = bad_resp.json()
    assert "detail" in error_data


@pytest.mark.asyncio
async def test_quality_rejection_path(async_client: AsyncClient):
    """Verifies quality failure path and recovery."""
    create_resp = await async_client.post(
        "/api/v1/sessions",
        json={"case_id": "CAS-GLARE-001", "operator_id": "OFC-15", "device_enrollment_id": "DEV-FIELD-01"},
    )
    session_id = create_resp.json()["id"]

    # DRAFT -> CAPTURED -> QUALITY_CHECKING
    await async_client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    await async_client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})

    # Quality check fails: QUALITY_CHECKING -> VALIDATION_FAILED
    fail_resp = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "VALIDATION_FAILED", "event_payload": {"reason": "SPECULAR_GLARE"}},
    )
    assert fail_resp.status_code == 200
    assert fail_resp.json()["status"] == "VALIDATION_FAILED"
    assert fail_resp.json()["measurement"]["quality_status"] == "FAIL"

    # Cannot jump from VALIDATION_FAILED to CLASSIFIED
    illegal_resp = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "CLASSIFIED"},
    )
    assert illegal_resp.status_code == 400

    # Retake capture: VALIDATION_FAILED -> CAPTURED
    retake_resp = await async_client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "CAPTURED"},
    )
    assert retake_resp.status_code == 200
    assert retake_resp.json()["status"] == "CAPTURED"


@pytest.mark.asyncio
async def test_profiles_listing(async_client: AsyncClient):
    """Verifies that registered assay profiles can be listed."""
    resp = await async_client.get("/api/v1/profiles")
    assert resp.status_code == 200
    profiles = resp.json()
    assert len(profiles) >= 3
    profile_ids = [p["profile_id"] for p in profiles]
    assert "marquis-standard-v1" in profile_ids
