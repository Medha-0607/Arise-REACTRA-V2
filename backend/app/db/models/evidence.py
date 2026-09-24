"""
SQLAlchemy ORM Model for Evidence Records.
Based on PRD Section 34.6.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    test_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    image_reference: Mapped[str | None] = mapped_column(String(256), nullable=True)
    image_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    canonical_record_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    record_digest: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signature: Mapped[str | None] = mapped_column(String(256), nullable=True)
    
    public_key_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signing_key_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_enrollment_id: Mapped[str] = mapped_column(String(64), default="DEV-OFFLINE-LOCAL", nullable=False)
    trust_registry_version: Mapped[str] = mapped_column(String(32), default="v1.0.0", nullable=False)
    
    signing_device_authorization_status: Mapped[str] = mapped_column(String(32), default="AUTHORIZED", nullable=False)
    previous_record_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    integrity_status: Mapped[str] = mapped_column(String(32), default="SEALED", nullable=False)
    
    sealed_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="evidence")
    custody_events: Mapped[list["CustodyEvent"]] = relationship("CustodyEvent", back_populates="evidence", cascade="all, delete-orphan")
