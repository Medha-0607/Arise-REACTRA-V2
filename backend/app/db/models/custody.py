"""
SQLAlchemy ORM Model for Custody Transfer Events.
Represents officer-recorded physical custody handoffs for sealed evidence.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CustodyEvent(Base):
    __tablename__ = "custody_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    evidence_id: Mapped[str] = mapped_column(String(64), ForeignKey("evidence_records.id", ondelete="CASCADE"), index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    
    sender_operator_id: Mapped[str] = mapped_column(String(64), nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(128), nullable=False)
    receiver_agency: Mapped[str] = mapped_column(String(128), nullable=False)
    receiver_badge_or_id: Mapped[str] = mapped_column(String(64), nullable=False)
    
    package_seal_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    transferred_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="custody_events")
    evidence: Mapped["EvidenceRecord"] = relationship("EvidenceRecord", back_populates="custody_events")
