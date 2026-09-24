"""REACTRA V2 — Procedural Context & Statutory Safeguards Service.

Coordinates retrieval, updating, post-seal immutability enforcement,
audit event logging, and laboratory referral triage aggregation.
Section Reference: PRD V2 §3.2, §34.5, §34.7.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models.audit import AuditEvent
from app.domain.identifiers import generate_event_id
from app.domain.state_machine import SessionState
from app.repositories.session_repository import SessionRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.procedural_repository import ProceduralRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.schemas.procedural import (
    ProceduralUpdateRequest,
    ProceduralContextResponse,
    ReferralSummaryResponse,
)


class ProceduralImmutabilityError(Exception):
    """Raised when an update is attempted on an immutably sealed session."""
    pass


class ProceduralService:
    """Service layer enforcing procedural context business rules and auditability."""

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditRepository(db)
        self.procedural_repo = ProceduralRepository(db)
        self.measurement_repo = MeasurementRepository(db)

    def get_procedural_context(self, session_id: str) -> ProceduralContextResponse:
        """Retrieve authoritative procedural context snapshot for a session."""
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        record = self.procedural_repo.get_by_session_id(session_id)
        is_sealed = (session.status == SessionState.EVIDENCE_SEALED.value)

        if not record:
            return ProceduralContextResponse(
                test_id=session_id,
                is_sealed=is_sealed,
                updated_at_utc=session.updated_at_utc,
            )

        return ProceduralContextResponse(
            test_id=record.test_id,
            kit_lot_number=record.kit_lot_number,
            kit_expiry_date=record.kit_expiry_date,
            search_context_type=record.search_context_type,
            authorization_reference=record.authorization_reference,
            panchnama_memo_ref_no=record.panchnama_memo_ref_no,
            panch_witness_1_name=record.panch_witness_1_name,
            panch_witness_2_name=record.panch_witness_2_name,
            procedural_safeguard_status=record.procedural_safeguard_status,
            section_50_status=record.section_50_status,
            section_50_choice_recorded=record.section_50_choice_recorded,
            gazetted_officer_or_magistrate_reference=record.gazetted_officer_or_magistrate_reference,
            inventory_ref_no=record.inventory_ref_no,
            section_52a_reference=record.section_52a_reference,
            sample_identifier=record.sample_identifier,
            seal_identifier=record.seal_identifier,
            sample_drawal_status=record.sample_drawal_status,
            magistrate_certification_status=record.magistrate_certification_status,
            section_57_report_ref_no=record.section_57_report_ref_no,
            section_57_report_status=record.section_57_report_status,
            officer_notes=record.officer_notes,
            is_sealed=is_sealed,
            updated_at_utc=record.updated_at_utc or session.updated_at_utc,
        )

    def update_procedural_context(
        self,
        session_id: str,
        data: ProceduralUpdateRequest,
        actor_id: Optional[str] = None,
    ) -> ProceduralContextResponse:
        """
        Update officer-supplied procedural metadata for an active session.
        
        Enforces:
        1. Session must exist.
        2. Session must NOT be in EVIDENCE_SEALED state.
        3. Updates database persistence.
        4. Appends tamper-evident audit event.
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # Post-Seal Immutability Enforcement
        if session.status == SessionState.EVIDENCE_SEALED.value:
            raise ProceduralImmutabilityError(
                f"Session '{session_id}' is immutably SEALED. Procedural context cannot be modified."
            )

        updated_record = self.procedural_repo.create_or_update(
            session_id=session_id,
            kit_lot_number=data.kit_lot_number,
            kit_expiry_date=data.kit_expiry_date,
            search_context_type=data.search_context_type,
            authorization_reference=data.authorization_reference,
            panchnama_memo_ref_no=data.panchnama_memo_ref_no,
            panch_witness_1_name=data.panch_witness_1_name,
            panch_witness_2_name=data.panch_witness_2_name,
            procedural_safeguard_status=data.procedural_safeguard_status,
            section_50_status=data.section_50_status,
            section_50_choice_recorded=data.section_50_choice_recorded,
            gazetted_officer_or_magistrate_reference=data.gazetted_officer_or_magistrate_reference,
            inventory_ref_no=data.inventory_ref_no,
            section_52a_reference=data.section_52a_reference,
            sample_identifier=data.sample_identifier,
            seal_identifier=data.seal_identifier,
            sample_drawal_status=data.sample_drawal_status,
            magistrate_certification_status=data.magistrate_certification_status,
            section_57_report_ref_no=data.section_57_report_ref_no,
            section_57_report_status=data.section_57_report_status,
            officer_notes=data.officer_notes,
        )

        effective_actor = actor_id or session.operator_id or "Operator"

        # Determine event type based on whether statutory safeguard choices were recorded
        event_type = (
            "SAFEGUARD_RECORDED"
            if (data.section_50_choice_recorded or data.section_52a_reference or data.section_57_report_ref_no)
            else "PROCEDURAL_CONTEXT_UPDATED"
        )

        payload_summary = {
            k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None
        }

        self.audit_repo.append(
            AuditEvent(
                event_id=generate_event_id(),
                test_id=session_id,
                event_type=event_type,
                from_state=session.status,
                to_state=session.status,
                actor_id=effective_actor,
                device_enrollment_id=session.device_enrollment_id or "DEV-OFFLINE-LOCAL",
                event_payload=payload_summary,
                event_timestamp_utc=datetime.now(timezone.utc),
            )
        )

        self.db.commit()

        return ProceduralContextResponse(
            test_id=updated_record.test_id,
            kit_lot_number=updated_record.kit_lot_number,
            kit_expiry_date=updated_record.kit_expiry_date,
            search_context_type=updated_record.search_context_type,
            authorization_reference=updated_record.authorization_reference,
            panchnama_memo_ref_no=updated_record.panchnama_memo_ref_no,
            panch_witness_1_name=updated_record.panch_witness_1_name,
            panch_witness_2_name=updated_record.panch_witness_2_name,
            procedural_safeguard_status=updated_record.procedural_safeguard_status,
            section_50_status=updated_record.section_50_status,
            section_50_choice_recorded=updated_record.section_50_choice_recorded,
            gazetted_officer_or_magistrate_reference=updated_record.gazetted_officer_or_magistrate_reference,
            inventory_ref_no=updated_record.inventory_ref_no,
            section_52a_reference=updated_record.section_52a_reference,
            sample_identifier=updated_record.sample_identifier,
            seal_identifier=updated_record.seal_identifier,
            sample_drawal_status=updated_record.sample_drawal_status,
            magistrate_certification_status=updated_record.magistrate_certification_status,
            section_57_report_ref_no=updated_record.section_57_report_ref_no,
            section_57_report_status=updated_record.section_57_report_status,
            officer_notes=updated_record.officer_notes,
            is_sealed=False,
            updated_at_utc=updated_record.updated_at_utc,
        )

    def get_referral_summary(self, session_id: str) -> ReferralSummaryResponse:
        """Aggregate authoritative triage summary data for laboratory handoff."""
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        procedural = self.procedural_repo.get_by_session_id(session_id)
        measurement = self.measurement_repo.get_measurement(session_id)
        evidence = session.evidence

        return ReferralSummaryResponse(
            session_id=session.id,
            case_id=session.case_id,
            event_id=session.event_id,
            operator_id=session.operator_id,
            field_officer_name=session.field_officer_name,
            police_station_jurisdiction=session.police_station_jurisdiction,
            assay_profile_id=session.assay_profile_id,
            assay_profile_version=session.assay_profile_version,
            presumptive_outcome=measurement.result if measurement else None,
            decision_margin=measurement.decision_margin if measurement else None,
            evidence_id=evidence.id if evidence else None,
            evidence_digest=evidence.record_digest if evidence else None,
            integrity_status=evidence.integrity_status if evidence else "UNSEALED",
            sample_identifier=procedural.sample_identifier if procedural else None,
            seal_identifier=procedural.seal_identifier if procedural else None,
            panchnama_memo_ref_no=procedural.panchnama_memo_ref_no if procedural else None,
            kit_lot_number=procedural.kit_lot_number if procedural else None,
            generated_at_utc=datetime.now(timezone.utc),
        )
