"""
SQLAlchemy ORM Model for Audit Events.
Based on PRD Section 34.7.
Append-only log of all state transitions and system operations.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    test_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    device_enrollment_id: Mapped[str] = mapped_column(String(64), default="DEV-OFFLINE-LOCAL", nullable=False)
    
    event_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    event_payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_event_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    event_timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="audit_events")
