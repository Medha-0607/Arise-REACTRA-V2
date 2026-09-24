"""REACTRA V2 — Evidence Sealing & Cryptographic Verification Test Suite.

Verifies:
1. Dynamic unique evidence identifier generation
2. Canonical JSON serialization & SHA-256 digest calculation
3. Ed25519 digital signing and verification
4. Mandatory 1-byte tamper detection test
5. Idempotent sealing behavior
6. Full end-to-end integration: CREATE -> MEASURE -> CLASSIFY -> SEAL -> VERIFY
"""

import json
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.domain.state_machine import SessionState
from app.scientific.profiles import STANDARD_GRID_PROFILE
from app.services.classification_service import register_validated_measurement
from app.services.evidence_service import EvidenceService
from app.schemas.evidence import EvidenceVerifyRequest
from tests.test_classifier import _make_dummy_measurement


def test_evidence_sealing_and_verification_unit():
    """Unit test: verify canonical JSON, SHA-256, Ed25519 signature verification."""
    envelope = {
        "format_version": "2.0.0",
        "evidence_id": "EVD-UNIT-001",
        "session_id": "SES-UNIT-001",
        "case_id": "CAS-UNIT-001",
        "operator_id": "OFC-001",
        "assay_profile_id": "marquis-standard-v1",
        "measurement": {
            "presumptive_result": "PRESUMPTIVE_POSITIVE",
            "decision_margin": 18.5,
        },
    }

    from app.security.hashing import canonicalize_json, calculate_sha256
    from app.security.signing import generate_device_keypair, sign_message
    from cryptography.hazmat.primitives import serialization

    priv, pub = generate_device_keypair()
    pub_hex = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()

    canonical_str = canonicalize_json(envelope)
    digest = calculate_sha256(canonical_str)
    sig = sign_message(priv, digest.encode("utf-8")).hex()

    # 1. Verify valid envelope
    req = EvidenceVerifyRequest(
        canonical_record_json=canonical_str,
        record_digest=digest,
        signature=sig,
        device_public_key_hex=pub_hex,
    )
    res = EvidenceService.verify_evidence(req)
    assert res.verification_status == "VERIFIED"
    assert res.digest_matches is True
    assert res.signature_valid is True

    # 2. Mandatory 1-Byte Tamper Test
    tampered_json = canonical_str.replace("PRESUMPTIVE_POSITIVE", "PRESUMPTIVE_NEGATIVE")
    req_tampered = EvidenceVerifyRequest(
        canonical_record_json=tampered_json,
        record_digest=digest,  # Original digest with modified payload
        signature=sig,
        device_public_key_hex=pub_hex,
    )
    res_tampered = EvidenceService.verify_evidence(req_tampered)
    assert res_tampered.verification_status == "TAMPER_DETECTED"
    assert res_tampered.digest_matches is False

    # 3. Invalid Signature Test
    corrupt_sig = sig[:-4] + "ffff"
    req_bad_sig = EvidenceVerifyRequest(
        canonical_record_json=canonical_str,
        record_digest=digest,
        signature=corrupt_sig,
        device_public_key_hex=pub_hex,
    )
    res_bad_sig = EvidenceService.verify_evidence(req_bad_sig)
    assert res_bad_sig.verification_status == "INVALID_SIGNATURE"
    assert res_bad_sig.digest_matches is True
    assert res_bad_sig.signature_valid is False


def test_full_workflow_measure_classify_seal_verify(db_session: Session):
    """End-to-End Test: Session -> Measure -> Classify -> Seal -> Verify API Endpoints."""
    client = TestClient(app)

    # 1. Create session
    create_res = client.post(
        "/api/v1/sessions",
        json={
            "case_id": "CAS-E2E-999",
            "operator_id": "OFC-E2E-1",
            "device_enrollment_id": "DEV-E2E-1",
            "assay_profile_id": "marquis-standard-v1",
            "capture_mode": "LIVE_CAMERA",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # 2. Transition through workflow
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "CAPTURED"})
    client.post(f"/api/v1/sessions/{session_id}/transition", json={"target_state": "QUALITY_CHECKING"})
    client.post(
        f"/api/v1/sessions/{session_id}/transition",
        json={"target_state": "READY_FOR_CLASSIFICATION", "quality_passed": True},
    )

    # Register measurement
    meas = _make_dummy_measurement(calibrated_well_lab=(35.0, 30.0, -15.0))
    meas.session_id = session_id
    register_validated_measurement(session_id, meas)

    # 3. Classify
    class_res = client.post(f"/api/v1/sessions/{session_id}/classify")
    assert class_res.status_code == 200
    assert class_res.json()["outcome"] == "PRESUMPTIVE_POSITIVE"
    assert class_res.json()["session_status"] == "CLASSIFIED"

    # 4. Seal Evidence
    seal_res = client.post(f"/api/v1/sessions/{session_id}/seal")
    assert seal_res.status_code == 200
    seal_data = seal_res.json()
    assert seal_data["session_id"] == session_id
    assert seal_data["integrity_status"] == "SEALED"
    assert seal_data["evidence_id"].startswith("EVD-")
    assert len(seal_data["record_digest"]) == 64
    assert len(seal_data["signature"]) > 32

    # 5. Verify Idempotency: Calling seal again returns the same sealed evidence
    seal_again_res = client.post(f"/api/v1/sessions/{session_id}/seal")
    assert seal_again_res.status_code == 200
    assert seal_again_res.json()["evidence_id"] == seal_data["evidence_id"]

    # 6. Verify Sealed Envelope via /api/v1/evidence/verify API
    verify_res = client.post(
        "/api/v1/evidence/verify",
        json={
            "canonical_record_json": seal_data["canonical_record_json"],
            "record_digest": seal_data["record_digest"],
            "signature": seal_data["signature"],
            "device_public_key_hex": seal_data["device_public_key_hex"],
        },
    )
    assert verify_res.status_code == 200
    ver_data = verify_res.json()
    assert ver_data["verification_status"] == "VERIFIED"
    assert ver_data["digest_matches"] is True
    assert ver_data["signature_valid"] is True

    # 7. Tamper verification check against API endpoint
    tampered_json = seal_data["canonical_record_json"][:-1] + " "
    tamper_api_res = client.post(
        "/api/v1/evidence/verify",
        json={
            "canonical_record_json": tampered_json,
            "record_digest": seal_data["record_digest"],
            "signature": seal_data["signature"],
            "device_public_key_hex": seal_data["device_public_key_hex"],
        },
    )
    assert tamper_api_res.status_code == 200
    assert tamper_api_res.json()["verification_status"] == "TAMPER_DETECTED"
