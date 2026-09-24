"""
SQLAlchemy ORM Model for Procedural Context.
Based on PRD Section 34.5.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProceduralContext(Base):
    __tablename__ = "procedural_context"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Kit & Batch Traceability
    kit_lot_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    kit_expiry_date: Mapped[str | None] = mapped_column(String(32), nullable=True)

    search_context_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    authorization_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    panchnama_memo_ref_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    panch_witness_1_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    panch_witness_2_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    procedural_safeguard_status: Mapped[str | None] = mapped_column(String(64), default="COMPLIANT", nullable=True)
    section_50_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    section_50_choice_recorded: Mapped[str | None] = mapped_column(String(64), nullable=True)
    gazetted_officer_or_magistrate_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    inventory_ref_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    section_52a_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sample_identifier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    seal_identifier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sample_drawal_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    magistrate_certification_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    section_57_report_ref_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    section_57_report_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    officer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    updated_at_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="procedural_context")
