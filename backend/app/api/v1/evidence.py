from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.evidence import (
    EvidenceVerifyRequest,
    EvidenceVerifyResponse,
    ChainVerificationResponse,
)
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("/verify", response_model=EvidenceVerifyResponse, status_code=status.HTTP_200_OK)
async def verify_evidence_envelope(req: EvidenceVerifyRequest) -> EvidenceVerifyResponse:
    """
    Cryptographically verifies an evidence envelope canonical record,
    SHA-256 payload digest, and Ed25519 digital signature.
    """
    return EvidenceService.verify_evidence(req)


@router.get("/chain/verify", response_model=ChainVerificationResponse, status_code=status.HTTP_200_OK)
async def verify_evidence_chain(
    device_enrollment_id: str = Query("DEV-OFFLINE-LOCAL", description="Device ID to verify hash chain for"),
    db: Session = Depends(get_db),
) -> ChainVerificationResponse:
    """
    Verifies the sequential inter-session cryptographic hash chain for a specific device.
    Detects chain discontinuities, reordered records, and signature/digest tampering.
    """
    return EvidenceService.verify_chain(db, device_enrollment_id=device_enrollment_id)

