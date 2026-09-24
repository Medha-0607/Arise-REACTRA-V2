"""REACTRA V2 — Evidence Sealing & Verification Schemas (Pydantic V2)."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class EvidenceSealResponse(BaseModel):
    session_id: str
    evidence_id: str
    canonical_record_json: str
    record_digest: str
    signature: str
    device_public_key_hex: str
    device_enrollment_id: str
    trust_registry_version: str
    integrity_status: str
    previous_record_hash: Optional[str] = None
    sealed_at_utc: str
    model_config = ConfigDict(from_attributes=True)


class EvidenceVerifyRequest(BaseModel):
    canonical_record_json: str
    record_digest: str
    signature: str
    device_public_key_hex: Optional[str] = None


class EvidenceVerifyResponse(BaseModel):
    verification_status: str  # VERIFIED, TAMPER_DETECTED, INVALID_SIGNATURE, INVALID_FORMAT
    digest_matches: bool
    signature_valid: bool
    recomputed_digest: str
    details: str
    model_config = ConfigDict(from_attributes=True)


class ChainVerificationItem(BaseModel):
    session_id: str
    evidence_id: str
    device_enrollment_id: str
    record_digest: str
    previous_record_hash: Optional[str] = None
    expected_previous_hash: Optional[str] = None
    digest_valid: bool
    signature_valid: bool
    chain_link_valid: bool
    sealed_at_utc: str


class ChainVerificationResponse(BaseModel):
    chain_status: str  # CHAIN_VALID, CHAIN_DISCONTINUITY, RECORD_ORDER_VIOLATION, EMPTY_CHAIN
    total_records_checked: int
    device_enrollment_id: str
    records: list[ChainVerificationItem]
    details: str
    model_config = ConfigDict(from_attributes=True)
