"""REACTRA V2 — Procedural Context, Statutory Safeguards & Referral Test Suite.

Verifies:
1. Procedural CRUD & persistence
2. Section 50 / 52A / 57 statutory reference metadata recording
3. Kit lot number & expiry date traceability
4. Append-only procedural audit event generation (PROCEDURAL_CONTEXT_UPDATED, SAFEGUARD_RECORDED)
5. Post-sealing immutability (modifying sealed session raises HTTP 409 Conflict)
6. Evidence envelope procedural snapshot binding and 1-byte tamper detection
7. Referral summary aggregation endpoint
8. History query filtering by case ID
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.services.classification_service import register_validated_measurement
from app.services.procedural_service import ProceduralImmutabilityError
from app.schemas.evidence import EvidenceVerifyRequest
from app.services.evidence_service import EvidenceService
from tests.test_classifier import _make_dummy_measurement


def test_procedural_context_crud_and_persistence(db_session: Session):
    """Test creating, retrieving, and updating procedural context."""
    client = TestClient(app)

    # 1. Create session
    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-PROC-001",
            "operator_id": "OFC-8492",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
            "capture_mode": "LIVE_CAMERA",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # 2. Get initial procedural context
    get_res = client.get(f"/api/v1/sessions/{session_id}/procedural")
    assert get_res.status_code == 200
    initial_proc = get_res.json()
    assert initial_proc["test_id"] == session_id
    assert initial_proc["is_sealed"] is False

    # 3. Update procedural context with witnesses, memo ref, and kit lot
    update_res = client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            "kit_lot_number": "LOT-MQ-2026-X4",
            "kit_expiry_date": "2027-10-31",
            "search_context_type": "PUBLIC_PLACE",
            "panchnama_memo_ref_no": "MEMO-2026-NDPS-101",
            "panch_witness_1_name": "Ramesh Kumar (Resident)",
            "panch_witness_2_name": "Suresh Patel (Resident)",
            "officer_notes": "Sample recovered from transparent polyethylene pouch.",
        },
    )
    assert update_res.status_code == 200
    updated_proc = update_res.json()
    assert updated_proc["kit_lot_number"] == "LOT-MQ-2026-X4"
    assert updated_proc["kit_expiry_date"] == "2027-10-31"
    assert updated_proc["panchnama_memo_ref_no"] == "MEMO-2026-NDPS-101"
    assert updated_proc["panch_witness_1_name"] == "Ramesh Kumar (Resident)"
    assert updated_proc["panch_witness_2_name"] == "Suresh Patel (Resident)"

    # 4. Verify persistence on subsequent GET
    get_again_res = client.get(f"/api/v1/sessions/{session_id}/procedural")
    assert get_again_res.status_code == 200
    assert get_again_res.json()["kit_lot_number"] == "LOT-MQ-2026-X4"


def test_statutory_safeguards_recording_section_50_52a_57(db_session: Session):
    """Test recording Section 50, 52A, and 57 statutory reference metadata."""
    client = TestClient(app)

    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-SAFEGUARD-002",
            "operator_id": "OFC-8492",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
            "capture_mode": "LIVE_CAMERA",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # Record statutory safeguard choices
    update_res = client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            # Section 50
            "section_50_status": "RECORDED",
            "section_50_choice_recorded": "GAZETTED_OFFICER",
            "gazetted_officer_or_magistrate_reference": "Shri V. Verma (Superintendent of Customs)",
            # Section 52A
            "inventory_ref_no": "INV-2026-52A-009",
            "section_52a_reference": "MAG-CERT-2026-44",
            "sample_identifier": "SMP-A1 / SMP-A2",
            "seal_identifier": "SEAL-CUSTOMS-88219",
            "sample_drawal_status": "DRAWN_IN_MAGISTRATE_PRESENCE",
            "magistrate_certification_status": "CERTIFIED",
            # Section 57
            "section_57_report_ref_no": "DISPATCH-57-2026-112",
            "section_57_report_status": "SUBMITTED",
        },
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["section_50_choice_recorded"] == "GAZETTED_OFFICER"
    assert data["gazetted_officer_or_magistrate_reference"] == "Shri V. Verma (Superintendent of Customs)"
    assert data["inventory_ref_no"] == "INV-2026-52A-009"
    assert data["sample_identifier"] == "SMP-A1 / SMP-A2"
    assert data["seal_identifier"] == "SEAL-CUSTOMS-88219"
    assert data["section_57_report_status"] == "SUBMITTED"


def test_procedural_audit_event_generation(db_session: Session):
    """Verify that procedural modifications generate immutable audit events visible in timeline."""
    client = TestClient(app)

    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-AUDIT-003",
            "operator_id": "OFC-AUDIT-1",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
        },
    )
    session_id = create_res.json()["id"]

    # Trigger update
    client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            "panchnama_memo_ref_no": "MEMO-AUDIT-99",
            "section_50_choice_recorded": "MAGISTRATE",
        },
    )

    # Check Timeline API for audit events
    timeline_res = client.get(f"/api/v1/sessions/{session_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()["events"]
    
    event_types = [e["event_type"] for e in events]
    assert "SESSION_CREATED" in event_types
    assert "SAFEGUARD_RECORDED" in event_types


def test_post_seal_procedural_immutability(db_session: Session):
    """Verify invariant: Procedural context cannot be modified once session is EVIDENCE_SEALED."""
    client = TestClient(app)

    # 1. Create and transition session to CLASSIFIED
    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-IMMUTABLE-004",
            "operator_id": "OFC-8492",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
        },
    )
    session_id = create_res.json()["id"]

    # Pre-seal procedural update (allowed)
    client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={"panchnama_memo_ref_no": "ORIGINAL-MEMO-REF"},
    )

    # Transition to READY_FOR_CLASSIFICATION
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )

    # Register measurement & Classify
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)
    client.post(f"/api/v1/sessions/{session_id}/classify")

    # Seal Evidence
    seal_res = client.post(f"/api/v1/sessions/{session_id}/seal")
    assert seal_res.status_code == 200

    # 2. Attempt post-seal procedural modification (MUST BE REJECTED with HTTP 409 Conflict)
    bad_update_res = client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={"panchnama_memo_ref_no": "ATTEMPTED-TAMPER-MEMO"},
    )
    assert bad_update_res.status_code == 409
    assert "SEALED" in bad_update_res.json()["detail"]

    # 3. Verify original procedural context remained unchanged
    get_res = client.get(f"/api/v1/sessions/{session_id}/procedural")
    assert get_res.json()["panchnama_memo_ref_no"] == "ORIGINAL-MEMO-REF"
    assert get_res.json()["is_sealed"] is True


def test_evidence_envelope_contains_procedural_snapshot_and_detects_tamper(db_session: Session):
    """Verify that sealed evidence envelope binds procedural context and detects tampering."""
    client = TestClient(app)

    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-SNAP-005",
            "operator_id": "OFC-8492",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
        },
    )
    session_id = create_res.json()["id"]

    # Populate procedural context before sealing
    client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            "kit_lot_number": "LOT-SEAL-VERIFY-1",
            "panchnama_memo_ref_no": "MEMO-SEAL-VERIFY-1",
            "section_50_choice_recorded": "GAZETTED_OFFICER",
        },
    )

    # Transition, measure, classify, seal
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)
    client.post(f"/api/v1/sessions/{session_id}/classify")

    seal_res = client.post(f"/api/v1/sessions/{session_id}/seal")
    assert seal_res.status_code == 200
    seal_data = seal_res.json()

    # 1. Verify canonical JSON contains procedural context
    canonical_json = seal_data["canonical_record_json"]
    assert "procedural_context" in canonical_json
    assert "LOT-SEAL-VERIFY-1" in canonical_json
    assert "MEMO-SEAL-VERIFY-1" in canonical_json
    assert "GAZETTED_OFFICER" in canonical_json

    # 2. Verify evidence verifies successfully
    verify_req = EvidenceVerifyRequest(
        canonical_record_json=seal_data["canonical_record_json"],
        record_digest=seal_data["record_digest"],
        signature=seal_data["signature"],
        device_public_key_hex=seal_data["device_public_key_hex"],
    )
    verify_res = EvidenceService.verify_evidence(verify_req)
    assert verify_res.verification_status == "VERIFIED"

    # 3. Tamper with procedural context in envelope -> verification must detect tampering
    tampered_json = canonical_json.replace("LOT-SEAL-VERIFY-1", "LOT-TAMPERED-99")
    tamper_req = EvidenceVerifyRequest(
        canonical_record_json=tampered_json,
        record_digest=seal_data["record_digest"],
        signature=seal_data["signature"],
        device_public_key_hex=seal_data["device_public_key_hex"],
    )
    tamper_res = EvidenceService.verify_evidence(tamper_req)
    assert tamper_res.verification_status == "TAMPER_DETECTED"
    assert tamper_res.digest_matches is False


def test_referral_summary_endpoint(db_session: Session):
    """Verify referral-summary endpoint returns authoritative triage summary."""
    client = TestClient(app)

    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-REF-006",
            "operator_id": "OFC-REF-1",
            "device_enrollment_id": "DEV-PROC-01",
            "field_officer_name": "Inspector R. Singh",
            "police_station_jurisdiction": "Crime Branch Special Cell",
            "assay_profile_id": "marquis-standard-v1",
        },
    )
    session_id = create_res.json()["id"]

    # Add procedural references
    client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            "sample_identifier": "SMP-REF-A1",
            "seal_identifier": "SEAL-REF-8841",
            "panchnama_memo_ref_no": "MEMO-REF-101",
            "kit_lot_number": "LOT-REF-99",
        },
    )

    # Transition, measure, classify, seal
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)
    client.post(f"/api/v1/sessions/{session_id}/classify")
    client.post(f"/api/v1/sessions/{session_id}/seal")

    # Fetch Referral Summary
    ref_res = client.get(f"/api/v1/sessions/{session_id}/referral-summary")
    assert ref_res.status_code == 200
    ref_data = ref_res.json()
    assert ref_data["session_id"] == session_id
    assert ref_data["case_id"] == "CAS-REF-006"
    assert ref_data["presumptive_outcome"] == "PRESUMPTIVE_POSITIVE"
    assert ref_data["sample_identifier"] == "SMP-REF-A1"
    assert ref_data["seal_identifier"] == "SEAL-REF-8841"
    assert ref_data["panchnama_memo_ref_no"] == "MEMO-REF-101"
    assert ref_data["kit_lot_number"] == "LOT-REF-99"
    assert ref_data["integrity_status"] == "SEALED"
    assert "PRESUMPTIVE FIELD TRIAGE DATA ONLY" in ref_data["disclaimer"]


def test_history_filtering_by_case_id(db_session: Session):
    """Verify history query filtering by case ID."""
    client = TestClient(app)

    case_target = "CAS-FILTER-TARGET-99"
    client.post(
        "/api/v1/sessions",
        json={
            "case_id": case_target,
            "operator_id": "OFC-HIST-1",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
        },
    )
    client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-OTHER-100",
            "operator_id": "OFC-HIST-2",
            "device_enrollment_id": "DEV-PROC-01",
            "assay_profile_id": "marquis-standard-v1",
        },
    )

    # Query with case_id filter
    list_res = client.get(f"/api/v1/sessions?case_id={case_target}")
    assert list_res.status_code == 200
    results = list_res.json()
    assert len(results) >= 1
    for r in results:
        assert r["case_id"] == case_target
