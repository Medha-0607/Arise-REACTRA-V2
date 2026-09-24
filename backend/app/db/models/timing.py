"""
SQLAlchemy ORM Model for Reaction Timing.
Based on PRD Section 34.2.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ReactionTiming(Base):
    __tablename__ = "reaction_timing"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    reaction_started_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capture_timestamp_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capture_elapsed_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    timer_source: Mapped[str] = mapped_column(String(32), default="MONOTONIC_LOCAL", nullable=False)
    kinetic_window_status: Mapped[str] = mapped_column(String(32), default="IN_WINDOW", nullable=False)
    
    t_min_seconds_snapshot: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    t_max_seconds_snapshot: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    reaction_start_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="timing")
