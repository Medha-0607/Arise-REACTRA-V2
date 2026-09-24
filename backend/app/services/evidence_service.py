"""REACTRA V2 — Authoritative Evidence Sealing & Verification Service.

Packages validated session metadata, measurement data, and presumptive classification
into a canonical JSON envelope, computes SHA-256 digest, and signs with device Ed25519 key.
Section References: PRD V2 §20-22, Master Build Spec §19-21.
"""

from typing import Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from app.db.models.audit import AuditEvent
from app.db.models.evidence import EvidenceRecord
from app.domain.identifiers import generate_event_id
from app.domain.state_machine import SessionState, SessionStateMachine, InvalidTransitionError
from app.repositories.session_repository import SessionRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.procedural_repository import ProceduralRepository
from app.security.hashing import canonicalize_json, calculate_sha256
from app.security.signing import generate_device_keypair, sign_message, verify_signature
from app.schemas.evidence import (
    EvidenceSealResponse,
    EvidenceVerifyRequest,
    EvidenceVerifyResponse,
    ChainVerificationItem,
    ChainVerificationResponse,
)

# Persistent device keypair instance for offline signing
_DEVICE_PRIVATE_KEY, _DEVICE_PUBLIC_KEY = generate_device_keypair()


def get_device_public_key_hex() -> str:
    """Returns raw hex encoding of device public key."""
    raw = _DEVICE_PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return raw.hex()


class EvidenceService:
    """Coordinates canonical packaging, cryptographic sealing, and verification."""

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditRepository(db)
        self.measurement_repo = MeasurementRepository(db)
        self.procedural_repo = ProceduralRepository(db)

    def seal_session(self, session_id: str) -> EvidenceSealResponse:
        """
        Cryptographically seals a classified session into a tamper-evident envelope.
        
        Enforces:
        1. Session must exist and have a valid classification outcome.
        2. Session must be in CLASSIFIED or REVIEW_REQUIRED state (idempotent if already SEALED).
        3. Retrieves preceding evidence record on the SAME device for monotonic hash chaining.
        4. Builds canonical JSON payload with dynamic evidence identifier & previous_record_hash.
        5. Calculates SHA-256 digest and creates Ed25519 digital signature.
        6. Persists EvidenceRecord in database.
        7. Transitions session to EVIDENCE_SEALED.
        8. Records audit event.
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # Idempotency check: if already sealed, return existing record
        existing_evidence = self.db.query(EvidenceRecord).filter(EvidenceRecord.test_id == session_id).first()
        if session.status == SessionState.EVIDENCE_SEALED.value and existing_evidence:
            return EvidenceSealResponse(
                session_id=session_id,
                evidence_id=existing_evidence.id,
                canonical_record_json=existing_evidence.canonical_record_json or "",
                record_digest=existing_evidence.record_digest or "",
                signature=existing_evidence.signature or "",
                device_public_key_hex=get_device_public_key_hex(),
                device_enrollment_id=existing_evidence.device_enrollment_id,
                trust_registry_version=existing_evidence.trust_registry_version,
                integrity_status=existing_evidence.integrity_status,
                previous_record_hash=existing_evidence.previous_record_hash,
                sealed_at_utc=existing_evidence.sealed_at_utc.isoformat(),
            )

        # 1. State Validation
        if session.status not in (SessionState.CLASSIFIED.value, SessionState.REVIEW_REQUIRED.value):
            raise InvalidTransitionError(
                session.status,
                SessionState.EVIDENCE_SEALED,
                reason="Session must be CLASSIFIED before it can be cryptographically sealed."
            )

        # 2. Measurement / Outcome Validation
        db_meas = self.measurement_repo.get_measurement(session_id)
        if not db_meas or not db_meas.result:
            raise ValueError(f"Session '{session_id}' has no classification outcome to seal.")

        now_utc = datetime.now(timezone.utc)
        evidence_id = f"EVD-{session_id[-8:]}-{int(now_utc.timestamp())}"

        # 3. Retrieve Preceding Evidence Record on the SAME Device for Hash Chaining
        device_id = session.device_enrollment_id or "DEV-OFFLINE-LOCAL"
        last_evidence = (
            self.db.query(EvidenceRecord)
            .filter(
                EvidenceRecord.device_enrollment_id == device_id,
                EvidenceRecord.test_id != session_id,
                EvidenceRecord.record_digest.isnot(None),
            )
            .order_by(EvidenceRecord.sealed_at_utc.desc())
            .first()
        )
        previous_record_hash = last_evidence.record_digest if last_evidence else None

        # 4. Retrieve Procedural Context Snapshot
        procedural_record = self.procedural_repo.get_by_session_id(session_id)
        procedural_dict = {}
        if procedural_record:
            procedural_dict = {
                "kit_lot_number": procedural_record.kit_lot_number,
                "kit_expiry_date": procedural_record.kit_expiry_date,
                "search_context_type": procedural_record.search_context_type,
                "authorization_reference": procedural_record.authorization_reference,
                "panchnama_memo_ref_no": procedural_record.panchnama_memo_ref_no,
                "panch_witness_1_name": procedural_record.panch_witness_1_name,
                "panch_witness_2_name": procedural_record.panch_witness_2_name,
                "procedural_safeguard_status": procedural_record.procedural_safeguard_status,
                "section_50_status": procedural_record.section_50_status,
                "section_50_choice_recorded": procedural_record.section_50_choice_recorded,
                "gazetted_officer_or_magistrate_reference": procedural_record.gazetted_officer_or_magistrate_reference,
                "inventory_ref_no": procedural_record.inventory_ref_no,
                "section_52a_reference": procedural_record.section_52a_reference,
                "sample_identifier": procedural_record.sample_identifier,
                "seal_identifier": procedural_record.seal_identifier,
                "sample_drawal_status": procedural_record.sample_drawal_status,
                "magistrate_certification_status": procedural_record.magistrate_certification_status,
                "section_57_report_ref_no": procedural_record.section_57_report_ref_no,
                "section_57_report_status": procedural_record.section_57_report_status,
                "officer_notes": procedural_record.officer_notes,
            }

        # 5. Build Canonical Envelope Dictionary (including previous_record_hash BEFORE signing)
        envelope_data = {
            "format_version": "2.0.0",
            "evidence_id": evidence_id,
            "session_id": session.id,
            "case_id": session.case_id,
            "operator_id": session.operator_id,
            "assay_profile_id": session.assay_profile_id,
            "assay_profile_version": session.assay_profile_version,
            "capture_mode": session.capture_mode,
            "gps_status": session.gps_status,
            "location_provenance": session.location_description or "Operator Declared (No GPS)",
            "device_enrollment_id": device_id,
            "previous_record_hash": previous_record_hash,
            "measurement": {
                "quality_status": db_meas.quality_status,
                "presumptive_result": db_meas.result,
                "class_distance_1": db_meas.class_distance_1,
                "class_distance_2": db_meas.class_distance_2,
                "decision_margin": db_meas.decision_margin,
                "calibration_residual": db_meas.calibration_residual,
                "lab_coordinates": [db_meas.reaction_lab_l, db_meas.reaction_lab_a, db_meas.reaction_lab_b],
            },
            "procedural_context": procedural_dict,
            "created_at_utc": session.created_at_utc.isoformat(),
            "sealed_at_utc": now_utc.isoformat(),
            "presumptive_disclaimer": (
                "Preliminary presumptive colorimetric indication only. Requires confirmatory "
                "laboratory testing (GC-MS/HPLC) for legal/evidentiary confirmation."
            ),
        }

        # 6. Canonicalize & Digest
        canonical_json_str = canonicalize_json(envelope_data)
        record_digest = calculate_sha256(canonical_json_str)

        # 7. Sign Digest with Ed25519
        sig_bytes = sign_message(_DEVICE_PRIVATE_KEY, record_digest.encode("utf-8"))
        signature_hex = sig_bytes.hex()
        pub_key_hex = get_device_public_key_hex()

        # 8. Persist EvidenceRecord
        signing_auth_status = (
            "UNENROLLED_DEMO_DEVICE" if device_id == "DEV-OFFLINE-LOCAL" else "OFFLINE_DEVICE_ENROLLED"
        )
        if existing_evidence:
            existing_evidence.canonical_record_json = canonical_json_str
            existing_evidence.record_digest = record_digest
            existing_evidence.signature = signature_hex
            existing_evidence.signing_key_fingerprint = pub_key_hex[:16]
            existing_evidence.device_enrollment_id = device_id
            existing_evidence.signing_device_authorization_status = signing_auth_status
            existing_evidence.previous_record_hash = previous_record_hash
            existing_evidence.sealed_at_utc = now_utc
            evidence_rec = existing_evidence
        else:
            evidence_rec = EvidenceRecord(
                id=evidence_id,
                test_id=session_id,
                canonical_record_json=canonical_json_str,
                record_digest=record_digest,
                signature=signature_hex,
                public_key_fingerprint=pub_key_hex[:16],
                signing_key_fingerprint=pub_key_hex[:16],
                device_enrollment_id=device_id,
                trust_registry_version="v1.0.0",
                signing_device_authorization_status=signing_auth_status,
                previous_record_hash=previous_record_hash,
                integrity_status="SEALED",
                sealed_at_utc=now_utc,
            )
            self.db.add(evidence_rec)

        # 9. State Transition
        SessionStateMachine.validate_transition(session.status, SessionState.EVIDENCE_SEALED)
        self.session_repo.update_status(session, SessionState.EVIDENCE_SEALED.value)

        # 10. Audit Event
        self.audit_repo.append(
            AuditEvent(
                event_id=generate_event_id(),
                test_id=session_id,
                event_type="EVIDENCE_SEALED",
                from_state=session.status,
                to_state=SessionState.EVIDENCE_SEALED.value,
                actor_id=session.operator_id or "Evidence Subsystem",
                device_enrollment_id=device_id,
                event_payload={
                    "evidence_id": evidence_id,
                    "record_digest": record_digest,
                    "previous_record_hash": previous_record_hash,
                    "signature": signature_hex[:32] + "...",
                },
                event_timestamp_utc=now_utc,
            )
        )

        self.db.commit()

        return EvidenceSealResponse(
            session_id=session_id,
            evidence_id=evidence_id,
            canonical_record_json=canonical_json_str,
            record_digest=record_digest,
            signature=signature_hex,
            device_public_key_hex=pub_key_hex,
            device_enrollment_id=device_id,
            trust_registry_version="v1.0.0",
            integrity_status="SEALED",
            previous_record_hash=previous_record_hash,
            sealed_at_utc=now_utc.isoformat(),
        )

    @classmethod
    def verify_evidence(cls, req: EvidenceVerifyRequest) -> EvidenceVerifyResponse:
        """
        Cryptographically verifies an evidence envelope payload.
        
        Checks:
        1. Canonical JSON representation and SHA-256 hash digest matching.
        2. Ed25519 digital signature validity against the device public key.
        
        Returns:
        - VERIFIED
        - TAMPER_DETECTED
        - INVALID_SIGNATURE
        - INVALID_FORMAT
        """
        # 1. Structural / Format Check
        if not req.canonical_record_json or not req.record_digest or not req.signature:
            return EvidenceVerifyResponse(
                verification_status="INVALID_FORMAT",
                digest_matches=False,
                signature_valid=False,
                recomputed_digest="",
                details="Missing required cryptographic parameters (canonical_record_json, record_digest, or signature)."
            )

        # 2. Recompute SHA-256 digest
        recomputed_digest = calculate_sha256(req.canonical_record_json)
        digest_matches = (recomputed_digest.lower() == req.record_digest.lower())

        if not digest_matches:
            return EvidenceVerifyResponse(
                verification_status="TAMPER_DETECTED",
                digest_matches=False,
                signature_valid=False,
                recomputed_digest=recomputed_digest,
                details=f"Payload digest mismatch: Expected {req.record_digest}, computed {recomputed_digest}. Record was altered."
            )

        # 3. Determine Public Key
        try:
            if req.device_public_key_hex:
                pub_key_bytes = bytes.fromhex(req.device_public_key_hex)
                public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)
            else:
                public_key = _DEVICE_PUBLIC_KEY
        except Exception as e:
            return EvidenceVerifyResponse(
                verification_status="INVALID_FORMAT",
                digest_matches=True,
                signature_valid=False,
                recomputed_digest=recomputed_digest,
                details=f"Invalid public key format: {str(e)}"
            )

        # 4. Verify Ed25519 Signature
        try:
            sig_bytes = bytes.fromhex(req.signature)
            sig_valid = verify_signature(public_key, sig_bytes, req.record_digest.encode("utf-8"))
        except Exception:
            sig_valid = False

        if not sig_valid:
            return EvidenceVerifyResponse(
                verification_status="INVALID_SIGNATURE",
                digest_matches=True,
                signature_valid=False,
                recomputed_digest=recomputed_digest,
                details="Ed25519 digital signature does not match device public key and digest."
            )

        return EvidenceVerifyResponse(
            verification_status="VERIFIED",
            digest_matches=True,
            signature_valid=True,
            recomputed_digest=recomputed_digest,
            details="Cryptographic envelope verified: SHA-256 digest matches and Ed25519 digital signature is valid."
        )

    @classmethod
    def verify_chain(
        cls, db: Session, device_enrollment_id: str = "DEV-OFFLINE-LOCAL"
    ) -> ChainVerificationResponse:
        """
        Cryptographically verifies the inter-session hash chain for a specific device.
        
        Checks:
        1. Monotonic chronological ordering (sealed_at_utc).
        2. Genesis record has previous_record_hash == None.
        3. Each subsequent record's previous_record_hash matches the immediately preceding record's record_digest.
        4. Canonical JSON SHA-256 digest matches stored record_digest for each record.
        5. Ed25519 signature is valid for each record.
        
        Returns:
        - CHAIN_VALID
        - CHAIN_DISCONTINUITY
        - RECORD_ORDER_VIOLATION
        - EMPTY_CHAIN
        """
        records = (
            db.query(EvidenceRecord)
            .filter(EvidenceRecord.device_enrollment_id == device_enrollment_id)
            .all()
        )

        if not records:
            return ChainVerificationResponse(
                chain_status="EMPTY_CHAIN",
                total_records_checked=0,
                device_enrollment_id=device_enrollment_id,
                records=[],
                details="No evidence records found for this device.",
            )

        # 1. Build lookup maps
        by_prev_hash: dict[str, EvidenceRecord] = {}
        genesis_records: list[EvidenceRecord] = []
        for r in records:
            if r.previous_record_hash is None:
                genesis_records.append(r)
            else:
                by_prev_hash[r.previous_record_hash.lower()] = r

        if len(genesis_records) != 1:
            # Missing or ambiguous genesis
            return ChainVerificationResponse(
                chain_status="CHAIN_DISCONTINUITY",
                total_records_checked=len(records),
                device_enrollment_id=device_enrollment_id,
                records=[],
                details=f"Device chain has {len(genesis_records)} genesis records (expected exactly 1).",
            )

        # 2. Traverse chain starting from genesis
        ordered_chain: list[EvidenceRecord] = []
        curr: Optional[EvidenceRecord] = genesis_records[0]
        visited_ids = set()

        while curr and curr.id not in visited_ids:
            visited_ids.add(curr.id)
            ordered_chain.append(curr)
            curr = by_prev_hash.get((curr.record_digest or "").lower())

        if len(ordered_chain) != len(records):
            # There are orphaned or disconnected records
            return ChainVerificationResponse(
                chain_status="CHAIN_DISCONTINUITY",
                total_records_checked=len(records),
                device_enrollment_id=device_enrollment_id,
                records=[],
                details=f"Discontinuity detected: {len(records) - len(ordered_chain)} orphaned/disconnected record(s) on device.",
            )

        # 3. Verify signatures, digests, and chronological monotonicity
        verification_items: list[ChainVerificationItem] = []
        chain_broken = False
        broken_reason = ""
        discontinuity_type = "CHAIN_VALID"

        for i, rec in enumerate(ordered_chain):
            computed_digest = calculate_sha256(rec.canonical_record_json or "")
            digest_valid = (computed_digest.lower() == (rec.record_digest or "").lower())

            pub_key = _DEVICE_PUBLIC_KEY
            try:
                sig_bytes = bytes.fromhex(rec.signature or "")
                sig_valid = verify_signature(pub_key, sig_bytes, (rec.record_digest or "").encode("utf-8"))
            except Exception:
                sig_valid = False

            if i == 0:
                expected_prev = None
                chain_link_valid = (rec.previous_record_hash is None)
            else:
                prev_rec = ordered_chain[i - 1]
                expected_prev = prev_rec.record_digest
                chain_link_valid = (
                    rec.previous_record_hash is not None
                    and rec.previous_record_hash.lower() == (expected_prev or "").lower()
                )

                # Check chronological monotonicity
                if rec.sealed_at_utc < prev_rec.sealed_at_utc:
                    chain_broken = True
                    discontinuity_type = "RECORD_ORDER_VIOLATION"
                    broken_reason = (
                        f"Record order violation at {rec.id}: timestamp ({rec.sealed_at_utc.isoformat()}) "
                        f"is earlier than preceding record {prev_rec.id} ({prev_rec.sealed_at_utc.isoformat()})."
                    )

            if not digest_valid or not sig_valid:
                if not chain_broken:
                    chain_broken = True
                    discontinuity_type = "CHAIN_DISCONTINUITY"
                    broken_reason = f"Cryptographic digest/signature verification failed at record {rec.id}."

            verification_items.append(
                ChainVerificationItem(
                    session_id=rec.test_id,
                    evidence_id=rec.id,
                    device_enrollment_id=rec.device_enrollment_id,
                    record_digest=rec.record_digest or "",
                    previous_record_hash=rec.previous_record_hash,
                    expected_previous_hash=expected_prev,
                    digest_valid=digest_valid,
                    signature_valid=sig_valid,
                    chain_link_valid=chain_link_valid,
                    sealed_at_utc=rec.sealed_at_utc.isoformat(),
                )
            )

        if not chain_broken:
            discontinuity_type = "CHAIN_VALID"
            broken_reason = f"All {len(ordered_chain)} evidence record(s) on device '{device_enrollment_id}' are valid and cryptographically linked."

        return ChainVerificationResponse(
            chain_status=discontinuity_type,
            total_records_checked=len(ordered_chain),
            device_enrollment_id=device_enrollment_id,
            records=verification_items,
            details=broken_reason,
        )

