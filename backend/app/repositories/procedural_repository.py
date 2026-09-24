"""REACTRA V2 — Procedural Context Repository.

Encapsulates database persistence and queries for the ProceduralContext entity.
Section Reference: PRD V2 §34.5.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.procedural import ProceduralContext


class ProceduralRepository:
    """Handles CRUD persistence for procedural safeguards and contextual field metadata."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_session_id(self, session_id: str) -> Optional[ProceduralContext]:
        """Retrieve procedural context for a given test session ID."""
        stmt = select(ProceduralContext).where(ProceduralContext.test_id == session_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create_or_update(
        self,
        session_id: str,
        kit_lot_number: Optional[str] = None,
        kit_expiry_date: Optional[str] = None,
        search_context_type: Optional[str] = None,
        authorization_reference: Optional[str] = None,
        panchnama_memo_ref_no: Optional[str] = None,
        panch_witness_1_name: Optional[str] = None,
        panch_witness_2_name: Optional[str] = None,
        procedural_safeguard_status: Optional[str] = None,
        section_50_status: Optional[str] = None,
        section_50_choice_recorded: Optional[str] = None,
        gazetted_officer_or_magistrate_reference: Optional[str] = None,
        inventory_ref_no: Optional[str] = None,
        section_52a_reference: Optional[str] = None,
        sample_identifier: Optional[str] = None,
        seal_identifier: Optional[str] = None,
        sample_drawal_status: Optional[str] = None,
        magistrate_certification_status: Optional[str] = None,
        section_57_report_ref_no: Optional[str] = None,
        section_57_report_status: Optional[str] = None,
        officer_notes: Optional[str] = None,
    ) -> ProceduralContext:
        """Create or update the authoritative ProceduralContext record for a session."""
        existing = self.get_by_session_id(session_id)
        now_utc = datetime.now(timezone.utc)

        if existing is None:
            existing = ProceduralContext(
                test_id=session_id,
                kit_lot_number=kit_lot_number,
                kit_expiry_date=kit_expiry_date,
                search_context_type=search_context_type,
                authorization_reference=authorization_reference,
                panchnama_memo_ref_no=panchnama_memo_ref_no,
                panch_witness_1_name=panch_witness_1_name,
                panch_witness_2_name=panch_witness_2_name,
                procedural_safeguard_status=procedural_safeguard_status or "COMPLIANT",
                section_50_status=section_50_status,
                section_50_choice_recorded=section_50_choice_recorded,
                gazetted_officer_or_magistrate_reference=gazetted_officer_or_magistrate_reference,
                inventory_ref_no=inventory_ref_no,
                section_52a_reference=section_52a_reference,
                sample_identifier=sample_identifier,
                seal_identifier=seal_identifier,
                sample_drawal_status=sample_drawal_status,
                magistrate_certification_status=magistrate_certification_status,
                section_57_report_ref_no=section_57_report_ref_no,
                section_57_report_status=section_57_report_status,
                officer_notes=officer_notes,
                updated_at_utc=now_utc,
            )
            self.db.add(existing)
        else:
            # Update fields only if provided (or preserve existing)
            if kit_lot_number is not None:
                existing.kit_lot_number = kit_lot_number
            if kit_expiry_date is not None:
                existing.kit_expiry_date = kit_expiry_date
            if search_context_type is not None:
                existing.search_context_type = search_context_type
            if authorization_reference is not None:
                existing.authorization_reference = authorization_reference
            if panchnama_memo_ref_no is not None:
                existing.panchnama_memo_ref_no = panchnama_memo_ref_no
            if panch_witness_1_name is not None:
                existing.panch_witness_1_name = panch_witness_1_name
            if panch_witness_2_name is not None:
                existing.panch_witness_2_name = panch_witness_2_name
            if procedural_safeguard_status is not None:
                existing.procedural_safeguard_status = procedural_safeguard_status
            if section_50_status is not None:
                existing.section_50_status = section_50_status
            if section_50_choice_recorded is not None:
                existing.section_50_choice_recorded = section_50_choice_recorded
            if gazetted_officer_or_magistrate_reference is not None:
                existing.gazetted_officer_or_magistrate_reference = gazetted_officer_or_magistrate_reference
            if inventory_ref_no is not None:
                existing.inventory_ref_no = inventory_ref_no
            if section_52a_reference is not None:
                existing.section_52a_reference = section_52a_reference
            if sample_identifier is not None:
                existing.sample_identifier = sample_identifier
            if seal_identifier is not None:
                existing.seal_identifier = seal_identifier
            if sample_drawal_status is not None:
                existing.sample_drawal_status = sample_drawal_status
            if magistrate_certification_status is not None:
                existing.magistrate_certification_status = magistrate_certification_status
            if section_57_report_ref_no is not None:
                existing.section_57_report_ref_no = section_57_report_ref_no
            if section_57_report_status is not None:
                existing.section_57_report_status = section_57_report_status
            if officer_notes is not None:
                existing.officer_notes = officer_notes
            existing.updated_at_utc = now_utc

        self.db.flush()
        return existing
