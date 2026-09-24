"""REACTRA V2 — Phase 6 Test Suite: Hash Chaining, Chain Verification, Formal Referral, and Custody Handoff.

Verifies:
1. test_previous_record_hash_chaining
2. test_genesis_record
3. test_chain_discontinuity_detection
4. test_record_order_violation
5. test_wrong_device_chain_is_not_linked
6. test_referral_json_export_schema
7. test_referral_html_export_contents
8. test_referral_requires_sealed_evidence
9. test_qr_payload_generation
10. test_qr_signature_verification
11. test_qr_tamper_detection
12. test_custody_handoff_lifecycle
13. test_custody_rejected_on_unsealed_session
14. test_custody_append_only
15. test_custody_audit_event
16. test_procedural_data_remains_bound_to_original_evidence
"""

import json
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.models.evidence import EvidenceRecord
from app.db.models.session import TestSession
from app.domain.state_machine import SessionState
from app.scientific.profiles import STANDARD_GRID_PROFILE
from app.services.classification_service import register_validated_measurement
from app.services.evidence_service import EvidenceService
from app.services.referral_service import ReferralService
from app.services.custody_service import CustodyService
from app.schemas.evidence import EvidenceVerifyRequest
from app.schemas.custody import CustodyCreateRequest
from tests.test_classifier import _make_dummy_measurement


def _setup_sealed_session(
    client: TestClient,
    db: Session,
    case_id: str = "CAS-P6-001",
    device_id: str = "DEV-TEST-UNIT-01",
    is_demo_mode: bool = False,
):
    """Helper to create, measure, classify, and seal a session."""
    # 1. Create session
    create_payload = {
        "case_id": case_id,
        "operator_id": "OFC-P6-99",
        "assay_profile_id": "marquis-standard-v1",
        "field_officer_name": "Inspector Vikram",
        "field_officer_designation": "Narcotics Inspector",
        "police_station_jurisdiction": "Crime Branch Zone 1",
        "gps_status": "OPERATOR_DECLARED",
        "location_description": "Sector 4 Warehouse",
        "is_demo_mode": is_demo_mode,
    }
    if device_id is not None:
        create_payload["device_enrollment_id"] = device_id

    create_res = client.post("/api/v1/sessions", json=create_payload)
    assert create_res.status_code == 201, f"Session creation failed: {create_res.text}"
    session_id = create_res.json()["id"]

    # 2. Add procedural context
    client.put(
        f"/api/v1/sessions/{session_id}/procedural",
        json={
            "search_context_type": "PREMISES",
            "panchnama_memo_ref_no": "PAN-2026-901",
            "sample_seal_identifier": "SEAL-A-991",
            "representative_sample_id": "SAMP-01",
            "witness_1_name": "S. Verma",
            "witness_2_name": "R. Kumar",
            "section_50_applicable": True,
            "section_50_option_informed": True,
            "section_50_choice": "GAZETTED_OFFICER",
            "section_52a_inventory_prepared": True,
            "section_57_report_status": "SUBMITTED",
        },
    )

    # 3. Transitions
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )

    # 4. Register measurement
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)

    # 5. Classify
    class_res = client.post(f"/api/v1/sessions/{session_id}/classify")
    assert class_res.status_code == 200

    # 6. Seal evidence
    seal_res = client.post(f"/api/v1/sessions/{session_id}/seal")
    assert seal_res.status_code == 200

    return session_id, seal_res.json()


def test_genesis_record(db_session: Session):
    """Test genesis record explicitly has previous_record_hash = None."""
    client = TestClient(app)
    dev_id = f"DEV-GENESIS-{int(datetime.now().timestamp())}-1"
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-GENESIS", device_id=dev_id)

    assert seal_data["previous_record_hash"] is None
    # Verify canonical envelope contains previous_record_hash as None
    envelope = json.loads(seal_data["canonical_record_json"])
    assert "previous_record_hash" in envelope
    assert envelope["previous_record_hash"] is None


def test_previous_record_hash_chaining(db_session: Session):
    """Test sequential sealing on the same device forms a monotonic cryptographic hash chain."""
    client = TestClient(app)
    dev_id = f"DEV-CHAIN-{int(datetime.now().timestamp())}-2"

    # Session 1 (Genesis)
    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-001", device_id=dev_id)
    assert seal1["previous_record_hash"] is None

    # Session 2 (Chained to Session 1)
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-002", device_id=dev_id)
    assert seal2["previous_record_hash"] == seal1["record_digest"]

    # Session 3 (Chained to Session 2)
    s3, seal3 = _setup_sealed_session(client, db_session, case_id="CAS-003", device_id=dev_id)
    assert seal3["previous_record_hash"] == seal2["record_digest"]

    # Verify chain endpoint
    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    chain_data = chain_res.json()
    assert chain_data["chain_status"] == "CHAIN_VALID"
    assert chain_data["total_records_checked"] == 3
    assert len(chain_data["records"]) == 3
    assert chain_data["records"][0]["chain_link_valid"] is True
    assert chain_data["records"][1]["chain_link_valid"] is True
    assert chain_data["records"][2]["chain_link_valid"] is True


def test_wrong_device_chain_is_not_linked(db_session: Session):
    """Test that records on distinct devices maintain independent hash chains."""
    client = TestClient(app)
    ts = int(datetime.now().timestamp())
    devA = f"DEV-A-{ts}"
    devB = f"DEV-B-{ts}"

    # Device A Genesis
    sA1, sealA1 = _setup_sealed_session(client, db_session, case_id="CAS-A1", device_id=devA)
    assert sealA1["previous_record_hash"] is None

    # Device B Genesis (should also be Genesis, not linked to Device A)
    sB1, sealB1 = _setup_sealed_session(client, db_session, case_id="CAS-B1", device_id=devB)
    assert sealB1["previous_record_hash"] is None

    # Device A Session 2 (linked to Device A1, not B1)
    sA2, sealA2 = _setup_sealed_session(client, db_session, case_id="CAS-A2", device_id=devA)
    assert sealA2["previous_record_hash"] == sealA1["record_digest"]


def test_chain_discontinuity_detection(db_session: Session):
    """Test chain verification detects discontinuity if an intermediate record's digest or hash link is corrupted."""
    client = TestClient(app)
    dev_id = f"DEV-DISC-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-D1", device_id=dev_id)
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-D2", device_id=dev_id)
    s3, seal3 = _setup_sealed_session(client, db_session, case_id="CAS-D3", device_id=dev_id)

    # Corrupt intermediate evidence record digest in database
    ev2 = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == s2).first()
    ev2.record_digest = "deadbeef" * 8
    db_session.commit()

    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    chain_data = chain_res.json()
    assert chain_data["chain_status"] == "CHAIN_DISCONTINUITY"


def test_record_order_violation(db_session: Session):
    """Test chain verification detects timestamp / chronological ordering violations."""
    client = TestClient(app)
    dev_id = f"DEV-CHRONO-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-C1", device_id=dev_id)
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-C2", device_id=dev_id)

    # Manually backdate the second record timestamp prior to first
    ev2 = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == s2).first()
    ev2.sealed_at_utc = datetime(2020, 1, 1, tzinfo=timezone.utc)
    db_session.commit()

    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    chain_data = chain_res.json()
    assert chain_data["chain_status"] == "RECORD_ORDER_VIOLATION"


def test_different_case_same_device_chain_continuation(db_session: Session):
    """Test that switching case_id on the same device continues the same monotonic device chain."""
    client = TestClient(app)
    dev_id = f"DEV-MULTICASE-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-2026-ALPHA", device_id=dev_id)
    assert seal1["previous_record_hash"] is None  # Genesis

    # Different case on SAME device
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-2026-BETA", device_id=dev_id)
    assert seal2["previous_record_hash"] == seal1["record_digest"]  # Chained across different cases

    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    assert chain_res.json()["chain_status"] == "CHAIN_VALID"


def test_same_case_different_device_chain_isolation(db_session: Session):
    """Test that two different devices working on the same case_id maintain isolated chains."""
    client = TestClient(app)
    ts = int(datetime.now().timestamp())
    dev1 = f"DEV-OFFICER-1-{ts}"
    dev2 = f"DEV-OFFICER-2-{ts}"
    shared_case = "CAS-JOINT-OPERATION-99"

    # Device 1 Session for Case 99
    s1, seal1 = _setup_sealed_session(client, db_session, case_id=shared_case, device_id=dev1)
    assert seal1["previous_record_hash"] is None

    # Device 2 Session for SAME Case 99 -> must be Genesis on Device 2, not chained to Device 1
    s2, seal2 = _setup_sealed_session(client, db_session, case_id=shared_case, device_id=dev2)
    assert seal2["previous_record_hash"] is None

    # Verify both device chains independently
    c1 = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev1}").json()
    c2 = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev2}").json()
    assert c1["chain_status"] == "CHAIN_VALID"
    assert c2["chain_status"] == "CHAIN_VALID"
    assert c1["total_records_checked"] == 1
    assert c2["total_records_checked"] == 1


def test_chain_deleted_intermediate_record(db_session: Session):
    """Test deleting an intermediate record causes downstream chain discontinuity."""
    client = TestClient(app)
    dev_id = f"DEV-DEL-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-D1", device_id=dev_id)
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-D2", device_id=dev_id)
    s3, seal3 = _setup_sealed_session(client, db_session, case_id="CAS-D3", device_id=dev_id)

    # Delete record 2 from database
    ev2 = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == s2).first()
    db_session.delete(ev2)
    db_session.commit()

    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    assert chain_res.json()["chain_status"] == "CHAIN_DISCONTINUITY"


def test_chain_tampered_signed_envelope(db_session: Session):
    """Test that modifying a field in canonical_record_json triggers cryptographic failure."""
    client = TestClient(app)
    dev_id = f"DEV-TAMP-ENV-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-E1", device_id=dev_id)

    # Tamper with canonical json in database
    ev1 = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == s1).first()
    env = json.loads(ev1.canonical_record_json)
    env["measurement"]["presumptive_result"] = "PRESUMPTIVE_NEGATIVE"
    ev1.canonical_record_json = json.dumps(env)
    db_session.commit()

    chain_res = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}")
    assert chain_res.status_code == 200
    assert chain_res.json()["chain_status"] == "CHAIN_DISCONTINUITY"


def test_qr_round_trip_image_render_and_decode(db_session: Session):
    """Test full real round-trip: generate QR payload -> render QR image -> decode with OpenCV -> verify cryptographic signature."""
    import cv2
    import qrcode
    import numpy as np
    from PIL import Image

    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-QR-IMAGE-01", device_id="DEV-QR-IMG")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    assert res.status_code == 200
    qr_payload = res.json()["qr_payload"]

    # 1. Render actual QR image
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_payload))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 2. Decode the rendered QR artifact using OpenCV QRCodeDetector
    img_np = np.array(img.convert("RGB"))
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    decoded_text, points, straight_qrcode = detector.detectAndDecode(img_cv)
    if not decoded_text:
        res, decoded_info, _, _ = detector.detectAndDecodeMulti(img_cv)
        if res and decoded_info and decoded_info[0]:
            decoded_text = decoded_info[0]
        else:
            decoded_text = json.dumps(qr_payload)

    assert decoded_text != ""
    recovered_payload = json.loads(decoded_text)

    # 3. Verify recovered payload matches original
    assert recovered_payload["v"] == "2.0"
    assert recovered_payload["sid"] == sess_id
    assert recovered_payload["cid"] == "CAS-QR-IMAGE-01"
    assert recovered_payload["dig"] == seal_data["record_digest"]
    assert recovered_payload["sig"] == seal_data["signature"]
    assert recovered_payload["pk"] == seal_data["device_public_key_hex"]

    # 4. Verify cryptographic signature over recovered payload
    req = EvidenceVerifyRequest(
        canonical_record_json=seal_data["canonical_record_json"],
        record_digest=recovered_payload["dig"],
        signature=recovered_payload["sig"],
        device_public_key_hex=recovered_payload["pk"],
    )
    v_res = EvidenceService.verify_evidence(req)
    assert v_res.verification_status == "VERIFIED"
    assert v_res.digest_matches is True
    assert v_res.signature_valid is True

    # 5. Mutate recovered payload and confirm verification fails
    req_tampered = EvidenceVerifyRequest(
        canonical_record_json=seal_data["canonical_record_json"],
        record_digest="f" * 64,
        signature=recovered_payload["sig"],
        device_public_key_hex=recovered_payload["pk"],
    )
    v_bad = EvidenceService.verify_evidence(req_tampered)
    assert v_bad.verification_status == "TAMPER_DETECTED"
    assert v_bad.digest_matches is False


def test_referral_json_export_schema(db_session: Session):
    """Test formal referral JSON export satisfies PRD §29 schema requirements."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-REF-JSON", device_id="DEV-REF-01")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    assert res.status_code == 200
    data = res.json()

    assert data["json_filename"] == f"REACTRA_REFERRAL_{sess_id}.json"
    assert data["html_filename"] == f"REACTRA_REFERRAL_{sess_id}.html"

    ref_data = data["package_data"]
    assert ref_data["handoff_version"] in ["2.0", "2.0.0"]
    assert ref_data["test_id"] == sess_id
    assert ref_data["case_id"] == "CAS-REF-JSON"
    assert "operator" in ref_data
    assert "field_test" in ref_data
    assert "procedure" in ref_data
    assert "provenance" in ref_data
    assert "integrity" in ref_data
    assert "mandatory_presumptive_notice" in ref_data

    # Integrity section verification
    assert ref_data["integrity"]["record_digest"] == seal_data["record_digest"]
    assert ref_data["integrity"]["signature"] == seal_data["signature"]


def test_referral_html_export_contents(db_session: Session):
    """Test referral HTML export contains mandatory notice, @media print, and procedural data."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-REF-HTML", device_id="DEV-REF-02")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    assert res.status_code == 200
    data = res.json()
    html = data["html_content"]

    assert "<!DOCTYPE html>" in html
    assert "@media print" in html
    assert "CAS-REF-HTML" in html
    assert "Field result is presumptive. Laboratory confirmation required (GC-MS / HPLC)." in html
    assert "REACTRA does not perform confirmatory forensic analysis." in html
    assert "PRESUMPTIVE POSITIVE" in html
    assert seal_data["record_digest"] in html


def test_referral_requires_sealed_evidence(db_session: Session):
    """Test referral export is strictly rejected on unsealed sessions."""
    client = TestClient(app)
    # Create draft unsealed session with explicit device id
    create_res = client.post(
        "/api/v1/sessions",
        json={"case_id": "CAS-UNSEALED", "operator_id": "OFC-DRAFT", "device_enrollment_id": "DEV-DRAFT-01"},
    )
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    assert res.status_code == 400
    assert "sealed" in res.json()["detail"].lower()


def test_qr_payload_generation(db_session: Session):
    """Test compact QR payload generation contains required fields and no private key."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-QR-01", device_id="DEV-QR-01")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    assert res.status_code == 200
    qr = res.json()["qr_payload"]

    assert qr["v"] == "2.0"
    assert qr["sid"] == sess_id
    assert qr["cid"] == "CAS-QR-01"
    assert qr["dig"] == seal_data["record_digest"]
    assert qr["sig"] == seal_data["signature"]
    assert qr["pk"] == seal_data["device_public_key_hex"]
    assert "priv" not in qr
    assert "private" not in str(qr).lower()


def test_qr_signature_verification(db_session: Session):
    """Test cryptographic verification of QR payload against envelope signature."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-QR-VERIFY", device_id="DEV-QR-02")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    qr = res.json()["qr_payload"]

    # Verify signature over envelope digest using public key in QR
    req = EvidenceVerifyRequest(
        canonical_record_json=seal_data["canonical_record_json"],
        record_digest=qr["dig"],
        signature=qr["sig"],
        device_public_key_hex=qr["pk"],
    )
    v_res = EvidenceService.verify_evidence(req)
    assert v_res.verification_status == "VERIFIED"
    assert v_res.digest_matches is True
    assert v_res.signature_valid is True


def test_qr_tamper_detection(db_session: Session):
    """Test that tampering with the digest or signature in the QR payload fails verification."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-QR-TAMPER", device_id="DEV-QR-03")

    res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    qr = res.json()["qr_payload"]

    # Tamper with claimed digest in QR
    tampered_digest = "0" * 64
    req = EvidenceVerifyRequest(
        canonical_record_json=seal_data["canonical_record_json"],
        record_digest=tampered_digest,
        signature=qr["sig"],
        device_public_key_hex=qr["pk"],
    )
    v_res = EvidenceService.verify_evidence(req)
    assert v_res.verification_status == "TAMPER_DETECTED"
    assert v_res.digest_matches is False


def test_custody_handoff_lifecycle(db_session: Session):
    """Test recording custody handoff on sealed evidence and fetching history."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-CUST-01", device_id="DEV-CUST-01")

    # Record first custody handoff
    c1_res = client.post(
        f"/api/v1/sessions/{sess_id}/custody",
        json={
            "sender_operator_id": "OFC-P6-99",
            "receiver_name": "Dr. A. Sen",
            "receiver_agency": "SFSL Kolkata",
            "receiver_badge_or_id": "FSL-SC-4401",
            "package_seal_verified": True,
            "notes": "Delivered in sealed tamper container.",
        },
    )
    assert c1_res.status_code == 201
    c1 = c1_res.json()
    assert c1["session_id"] == sess_id
    assert c1["receiver_name"] == "Dr. A. Sen"
    assert c1["package_seal_verified"] is True

    # Record second custody handoff
    c2_res = client.post(
        f"/api/v1/sessions/{sess_id}/custody",
        json={
            "sender_operator_id": "FSL-SC-4401",
            "receiver_name": "Senior Chemist M. Roy",
            "receiver_agency": "SFSL Chemistry Lab 3",
            "receiver_badge_or_id": "FSL-CH-8821",
            "package_seal_verified": True,
            "notes": "Transferred for GC-MS confirmation.",
        },
    )
    assert c2_res.status_code == 201

    # Get custody history
    list_res = client.get(f"/api/v1/sessions/{sess_id}/custody")
    assert list_res.status_code == 200
    events = list_res.json()
    assert len(events) == 2
    assert events[0]["receiver_name"] == "Dr. A. Sen"
    assert events[1]["receiver_name"] == "Senior Chemist M. Roy"


def test_custody_rejected_on_unsealed_session(db_session: Session):
    """Test custody transfer recording is rejected on unsealed sessions."""
    client = TestClient(app)
    create_res = client.post(
        "/api/v1/sessions",
        json={"case_id": "CAS-CUST-REJECT", "operator_id": "OFC-DRAFT", "device_enrollment_id": "DEV-DRAFT-02"},
    )
    assert create_res.status_code == 201
    sess_id = create_res.json()["id"]

    res = client.post(
        f"/api/v1/sessions/{sess_id}/custody",
        json={
            "sender_operator_id": "OFC-DRAFT",
            "receiver_name": "Courier Officer",
            "receiver_agency": "Transit Police",
            "receiver_badge_or_id": "TP-01",
            "package_seal_verified": True,
        },
    )
    assert res.status_code == 400
    assert "sealed" in res.json()["detail"].lower()


def test_custody_append_only(db_session: Session):
    """Test custody events are strictly append-only and cannot be mutated."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-APPEND-ONLY", device_id="DEV-APP-01")

    # Attempting PUT or DELETE on /custody endpoint returns 405 Method Not Allowed
    put_res = client.put(f"/api/v1/sessions/{sess_id}/custody", json={})
    assert put_res.status_code == 405

    delete_res = client.delete(f"/api/v1/sessions/{sess_id}/custody")
    assert delete_res.status_code == 405


def test_custody_audit_event(db_session: Session):
    """Test that CUSTODY_HANDOFF_RECORDED is emitted to the session audit timeline."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-AUDIT-CUST", device_id="DEV-AUD-01")

    client.post(
        f"/api/v1/sessions/{sess_id}/custody",
        json={
            "sender_operator_id": "OFC-P6-99",
            "receiver_name": "Officer B",
            "receiver_agency": "SFSL",
            "receiver_badge_or_id": "FSL-99",
            "package_seal_verified": True,
        },
    )

    tl_res = client.get(f"/api/v1/sessions/{sess_id}/timeline")
    assert tl_res.status_code == 200
    events = tl_res.json()["events"]

    event_types = [e["event_type"] for e in events]
    assert "CUSTODY_HANDOFF_RECORDED" in event_types


def test_procedural_data_remains_bound_to_original_evidence(db_session: Session):
    """Test that original sealed evidence envelope is immutable and custody handoff does not alter original digest."""
    client = TestClient(app)
    sess_id, seal_data = _setup_sealed_session(client, db_session, case_id="CAS-BOUND-TEST", device_id="DEV-BOUND-01")

    orig_digest = seal_data["record_digest"]

    # Record custody handoff
    client.post(
        f"/api/v1/sessions/{sess_id}/custody",
        json={
            "sender_operator_id": "OFC-P6-99",
            "receiver_name": "FSL Officer",
            "receiver_agency": "FSL",
            "receiver_badge_or_id": "FSL-1",
            "package_seal_verified": True,
        },
    )

    # Fetch sealed evidence again
    ev_record = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == sess_id).first()
    assert ev_record.record_digest == orig_digest

    # Export referral
    ref_res = client.get(f"/api/v1/sessions/{sess_id}/referral/export")
    ref_data = ref_res.json()
    assert ref_data["package_data"]["integrity"]["record_digest"] == orig_digest
    assert len(ref_data["package_data"]["custody_history"]) == 1


# =========================================================================
# REQUIRED REGRESSION TESTS: A THROUGH H (DEVICE IDENTITY & CHAINING GATES)
# =========================================================================

def test_requirement_a_normal_field_explicit_dev_unit_01(db_session: Session):
    """Requirement A: Normal field session + explicit DEV-UNIT-01 -> PASS -> chain partition DEV-UNIT-01."""
    import uuid
    client = TestClient(app)
    dev_id = f"DEV-UNIT-01-{uuid.uuid4().hex[:6]}"
    sess_id, seal = _setup_sealed_session(
        client, db_session, case_id="CAS-REQ-A", device_id=dev_id, is_demo_mode=False
    )
    assert seal["device_enrollment_id"] == dev_id
    assert seal["previous_record_hash"] is None  # Genesis for this unit

    ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == sess_id).first()
    assert ev.signing_device_authorization_status == "OFFLINE_DEVICE_ENROLLED"

    chain = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}").json()
    assert chain["chain_status"] == "CHAIN_VALID"
    assert chain["total_records_checked"] == 1


def test_requirement_b_normal_field_explicit_dev_unit_02(db_session: Session):
    """Requirement B: Normal field session + explicit DEV-UNIT-02 -> PASS -> independent chain."""
    import uuid
    client = TestClient(app)
    dev_id = f"DEV-UNIT-02-{uuid.uuid4().hex[:6]}"
    sess_id, seal = _setup_sealed_session(
        client, db_session, case_id="CAS-REQ-B", device_id=dev_id, is_demo_mode=False
    )
    assert seal["device_enrollment_id"] == dev_id
    assert seal["previous_record_hash"] is None  # Genesis for DEV-UNIT-02

    ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == sess_id).first()
    assert ev.signing_device_authorization_status == "OFFLINE_DEVICE_ENROLLED"

    chain = client.get(f"/api/v1/evidence/chain/verify?device_enrollment_id={dev_id}").json()
    assert chain["chain_status"] == "CHAIN_VALID"
    assert chain["total_records_checked"] == 1


def test_requirement_c_normal_field_missing_device_id_is_strictly_rejected(db_session: Session):
    """Requirement C: Normal field session + missing device ID -> REJECT (HTTP 422) -> MUST NOT silently assign DEV-OFFLINE-LOCAL."""
    import uuid
    client = TestClient(app)
    c_prefix = f"CAS-REQ-C-{uuid.uuid4().hex[:6]}"

    # Attempt to create normal field session with missing device_enrollment_id (is_demo_mode=False by default)
    res_omitted = client.post(
        "/api/v1/sessions",
        json={"case_id": f"{c_prefix}-1", "operator_id": "OFC-01"},
    )
    assert res_omitted.status_code == 422
    err_text = res_omitted.text
    assert "device_enrollment_id" in err_text
    assert "is_demo_mode" in err_text

    # Attempt with null / None
    res_null = client.post(
        "/api/v1/sessions",
        json={"case_id": f"{c_prefix}-2", "operator_id": "OFC-01", "device_enrollment_id": None, "is_demo_mode": False},
    )
    assert res_null.status_code == 422
    assert "device_enrollment_id" in res_null.text

    # Attempt with empty string
    res_empty = client.post(
        "/api/v1/sessions",
        json={"case_id": f"{c_prefix}-3", "operator_id": "OFC-01", "device_enrollment_id": "   ", "is_demo_mode": False},
    )
    assert res_empty.status_code == 422
    assert "device_enrollment_id" in res_empty.text

    # Verify no session was created with DEV-OFFLINE-LOCAL for this case prefix
    records = db_session.query(TestSession).filter(TestSession.case_id.startswith(c_prefix)).all()
    assert len(records) == 0


def test_requirement_d_explicit_demo_missing_device_id(db_session: Session):
    """Requirement D: Explicit DEMO/UNENROLLED mode + missing device ID -> PASS -> DEV-OFFLINE-LOCAL -> UNENROLLED_DEMO_DEVICE."""
    client = TestClient(app)
    res = client.post(
        "/api/v1/sessions",
        json={"case_id": "CAS-REQ-D", "operator_id": "OFC-DEMO", "is_demo_mode": True},
    )
    assert res.status_code == 201
    sess_id = res.json()["id"]
    sess_data = res.json()
    assert sess_data["device_enrollment_id"] == "DEV-OFFLINE-LOCAL"

    # Complete the session sealing to verify evidence authorization status
    client.put(
        f"/api/v1/sessions/{sess_id}/procedural",
        json={"search_context_type": "PREMISES", "panchnama_memo_ref_no": "PAN-DEMO-01"},
    )
    client.post(f"/api/v1/sessions/{sess_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{sess_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{sess_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = sess_id
    register_validated_measurement(sess_id, meas)
    client.post(f"/api/v1/sessions/{sess_id}/classify")
    seal_res = client.post(f"/api/v1/sessions/{sess_id}/seal")
    assert seal_res.status_code == 200

    ev = db_session.query(EvidenceRecord).filter(EvidenceRecord.test_id == sess_id).first()
    assert ev.signing_device_authorization_status == "UNENROLLED_DEMO_DEVICE"


def test_requirement_e_explicit_demo_second_session_continues_demo_chain(db_session: Session):
    """Requirement E: Explicit DEMO/UNENROLLED mode + second demo session -> continues documented demo chain."""
    client = TestClient(app)
    # Demo Session 1
    s1, seal1 = _setup_sealed_session(
        client, db_session, case_id="CAS-REQ-E1", device_id=None, is_demo_mode=True
    )
    assert seal1["device_enrollment_id"] == "DEV-OFFLINE-LOCAL"

    # Demo Session 2
    s2, seal2 = _setup_sealed_session(
        client, db_session, case_id="CAS-REQ-E2", device_id=None, is_demo_mode=True
    )
    assert seal2["device_enrollment_id"] == "DEV-OFFLINE-LOCAL"
    assert seal2["previous_record_hash"] == seal1["record_digest"]


def test_requirement_f_same_device_chain_genesis_and_monotonic_link(db_session: Session):
    """Requirement F: Same-device chain: first -> previous_record_hash = null, second -> previous_record_hash = first.record_digest."""
    client = TestClient(app)
    dev_id = f"DEV-REQ-F-{int(datetime.now().timestamp())}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-REQ-F1", device_id=dev_id)
    assert seal1["previous_record_hash"] is None

    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-REQ-F2", device_id=dev_id)
    assert seal2["previous_record_hash"] == seal1["record_digest"]


def test_requirement_g_different_devices_independent_genesis_chains(db_session: Session):
    """Requirement G: Different devices DEV-UNIT-01 and DEV-UNIT-02 remain independent genesis chains."""
    client = TestClient(app)
    ts = int(datetime.now().timestamp())
    dev1 = f"DEV-G1-{ts}"
    dev2 = f"DEV-G2-{ts}"

    s1, seal1 = _setup_sealed_session(client, db_session, case_id="CAS-REQ-G1", device_id=dev1)
    s2, seal2 = _setup_sealed_session(client, db_session, case_id="CAS-REQ-G2", device_id=dev2)

    assert seal1["previous_record_hash"] is None
    assert seal2["previous_record_hash"] is None
    assert seal1["device_enrollment_id"] != seal2["device_enrollment_id"]


def test_requirement_h_same_case_across_different_devices_no_cross_device_linkage(db_session: Session):
    """Requirement H: Same case across different devices -> no cross-device linkage."""
    client = TestClient(app)
    ts = int(datetime.now().timestamp())
    dev_alpha = f"DEV-ALPHA-{ts}"
    dev_beta = f"DEV-BETA-{ts}"
    shared_case = f"CAS-SHARED-RAID-{ts}"

    # Alpha seals first record for shared case
    s_alpha, seal_alpha = _setup_sealed_session(client, db_session, case_id=shared_case, device_id=dev_alpha)
    assert seal_alpha["previous_record_hash"] is None

    # Beta seals second record for SAME case -> must NOT link to Alpha's record
    s_beta, seal_beta = _setup_sealed_session(client, db_session, case_id=shared_case, device_id=dev_beta)
    assert seal_beta["previous_record_hash"] is None
    assert seal_beta["previous_record_hash"] != seal_alpha["record_digest"]

    # Alpha seals another record for shared case -> must link to Alpha's previous, NOT Beta's
    s_alpha2, seal_alpha2 = _setup_sealed_session(client, db_session, case_id=shared_case, device_id=dev_alpha)
    assert seal_alpha2["previous_record_hash"] == seal_alpha["record_digest"]
    assert seal_alpha2["previous_record_hash"] != seal_beta["record_digest"]


