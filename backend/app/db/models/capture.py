"""
SQLAlchemy ORM Model for Capture Records.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CaptureRecord(Base):
    __tablename__ = "capture_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    
    provenance: Mapped[str] = mapped_column(String(32), default="LIVE_CAMERA", nullable=False)
    image_path: Mapped[str] = mapped_column(String(256), nullable=False)
    image_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    
    quality_status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    captured_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="captures")
