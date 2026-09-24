"""
SQLAlchemy ORM Models for Device Enrollments and Trusted Key Registry.
Based on PRD Section 34.8 & 34.9.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DeviceEnrollment(Base):
    __tablename__ = "device_enrollments"

    device_enrollment_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    device_platform: Mapped[str] = mapped_column(String(64), default="LOCAL_FIELD_TABLET", nullable=False)
    device_attestation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    public_key_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    
    issuer_id: Mapped[str] = mapped_column(String(64), default="AUTHORITY_ROOT", nullable=False)
    registry_version: Mapped[str] = mapped_column(String(32), default="v1.0.0", nullable=False)
    
    enrolled_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    valid_from_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    valid_until_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    revoked_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    enrollment_record_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)


class TrustedKeyRegistry(Base):
    __tablename__ = "trusted_key_registry"

    registry_version: Mapped[str] = mapped_column(String(32), primary_key=True)
    issuer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    registry_payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    registry_signature: Mapped[str] = mapped_column(String(256), nullable=False)
    authority_key_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
