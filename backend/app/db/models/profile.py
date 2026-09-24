"""
SQLAlchemy ORM Model for Assay Profiles.
Based on PRD Section 34.4.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AssayProfile(Base):
    __tablename__ = "assay_profiles"

    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    profile_name: Mapped[str] = mapped_column(String(128), nullable=False)
    profile_version: Mapped[str] = mapped_column(String(32), primary_key=True, default="v1.0.0")
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    manufacturer_or_source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reference_card_version: Mapped[str] = mapped_column(String(64), default="ref-card-grid-3x2", nullable=False)
    
    # Timing & Reaction Curves
    t_min_seconds: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    t_max_seconds: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    kinetic_window_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Configurations
    threshold_configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    calibration_targets: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    classifier_configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reaction_start_definition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reaction_roi_definition: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Validity Period & Hash
    profile_effective_from_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    profile_effective_until_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_snapshot_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
