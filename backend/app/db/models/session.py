"""
SQLAlchemy ORM Model for Test Sessions.
Based on PRD Section 34.1 & Master Build Spec.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_id: Mapped[str] = mapped_column(String(64), nullable=True)
    operator_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    field_officer_name: Mapped[str] = mapped_column(String(128), nullable=True)
    field_officer_designation: Mapped[str] = mapped_column(String(64), nullable=True)
    police_station_jurisdiction: Mapped[str] = mapped_column(String(128), nullable=True)
    
    # Immutable Profile Binding
    assay_profile_id: Mapped[str] = mapped_column(String(64), nullable=False)
    assay_profile_version: Mapped[str] = mapped_column(String(32), nullable=False)
    
    # Authoritative Workflow Status
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", index=True, nullable=False)
    capture_mode: Mapped[str] = mapped_column(String(32), default="LIVE_CAMERA", nullable=False)
    
    # Provenance & Location (Strict: never fabricated)
    gps_status: Mapped[str] = mapped_column(String(32), default="OPERATOR_DECLARED", nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    
    # Local Sync & Enrollment Metadata
    sync_state: Mapped[str] = mapped_column(String(32), default="LOCAL_ONLY", nullable=False)
    device_enrollment_id: Mapped[str] = mapped_column(String(64), default="DEV-OFFLINE-LOCAL", nullable=False)
    signing_key_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    # Timestamps
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    timing: Mapped["ReactionTiming"] = relationship("ReactionTiming", back_populates="session", uselist=False, cascade="all, delete-orphan")
    measurement: Mapped["MeasurementResult"] = relationship("MeasurementResult", back_populates="session", uselist=False, cascade="all, delete-orphan")
    procedural_context: Mapped["ProceduralContext"] = relationship("ProceduralContext", back_populates="session", uselist=False, cascade="all, delete-orphan")
    captures: Mapped[list["CaptureRecord"]] = relationship("CaptureRecord", back_populates="session", cascade="all, delete-orphan")
    evidence: Mapped["EvidenceRecord"] = relationship("EvidenceRecord", back_populates="session", uselist=False, cascade="all, delete-orphan")
    custody_events: Mapped[list["CustodyEvent"]] = relationship("CustodyEvent", back_populates="session", cascade="all, delete-orphan")
    audit_events: Mapped[list["AuditEvent"]] = relationship("AuditEvent", back_populates="session", cascade="all, delete-orphan")
