"""REACTRA V2 — Procedural Context & Referral Schemas (Pydantic V2).

Defines validation and serialization models for procedural safeguards,
statutory references (NDPS Section 50/52A/57), kit lot tracking, and referral triage summaries.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProceduralUpdateRequest(BaseModel):
    """Payload for updating officer-supplied procedural metadata."""
    kit_lot_number: Optional[str] = Field(None, description="Chemical reagent test kit lot / batch number")
    kit_expiry_date: Optional[str] = Field(None, description="Test kit expiration date string (YYYY-MM-DD)")
    
    search_context_type: Optional[str] = Field(None, description="Search context (e.g. PUBLIC_PLACE, CONVEYANCE, PERSONAL_SEARCH, PREMISES)")
    authorization_reference: Optional[str] = Field(None, description="Statutory search warrant or authorization reference number")
    panchnama_memo_ref_no: Optional[str] = Field(None, description="Seizure memo / panchnama memo reference number")
    panch_witness_1_name: Optional[str] = Field(None, description="First independent witness name")
    panch_witness_2_name: Optional[str] = Field(None, description="Second independent witness name")
    
    procedural_safeguard_status: Optional[str] = Field(None, description="Safeguard tracking status (COMPLIANT, EXCEPTION_NOTED, NOT_APPLICABLE)")
    
    # Section 50 Personal Search
    section_50_status: Optional[str] = Field(None, description="Section 50 status (e.g. RECORDED, NOT_APPLICABLE, PENDING)")
    section_50_choice_recorded: Optional[str] = Field(None, description="Officer-recorded choice (GAZETTED_OFFICER, MAGISTRATE, DECLINED, NOT_APPLICABLE)")
    gazetted_officer_or_magistrate_reference: Optional[str] = Field(None, description="Reference/Name of Gazetted Officer or Magistrate")
    
    # Section 52A Magisterial Inventory & Sampling
    inventory_ref_no: Optional[str] = Field(None, description="Seizure inventory reference number")
    section_52a_reference: Optional[str] = Field(None, description="Section 52A Magisterial certification memo reference")
    sample_identifier: Optional[str] = Field(None, description="Representative sample package identifier (e.g. SMP-A1)")
    seal_identifier: Optional[str] = Field(None, description="Forensic tamper seal identifier (e.g. SL-88219)")
    sample_drawal_status: Optional[str] = Field(None, description="Sample drawal status (DRAWN_IN_MAGISTRATE_PRESENCE, PENDING)")
    magistrate_certification_status: Optional[str] = Field(None, description="Magistrate inventory certification status (CERTIFIED, PENDING)")
    
    # Section 57 Report to Immediate Superior
    section_57_report_ref_no: Optional[str] = Field(None, description="Section 57 report dispatch reference number")
    section_57_report_status: Optional[str] = Field(None, description="Section 57 report status (SUBMITTED, PENDING, DISPATCHED)")
    
    officer_notes: Optional[str] = Field(None, description="General field notes entered by officer")


class ProceduralContextResponse(BaseModel):
    """Authoritative response containing full procedural context snapshot."""
    test_id: str
    kit_lot_number: Optional[str] = None
    kit_expiry_date: Optional[str] = None
    search_context_type: Optional[str] = None
    authorization_reference: Optional[str] = None
    panchnama_memo_ref_no: Optional[str] = None
    panch_witness_1_name: Optional[str] = None
    panch_witness_2_name: Optional[str] = None
    procedural_safeguard_status: Optional[str] = "COMPLIANT"
    
    section_50_status: Optional[str] = None
    section_50_choice_recorded: Optional[str] = None
    gazetted_officer_or_magistrate_reference: Optional[str] = None
    
    inventory_ref_no: Optional[str] = None
    section_52a_reference: Optional[str] = None
    sample_identifier: Optional[str] = None
    seal_identifier: Optional[str] = None
    sample_drawal_status: Optional[str] = None
    magistrate_certification_status: Optional[str] = None
    
    section_57_report_ref_no: Optional[str] = None
    section_57_report_status: Optional[str] = None
    officer_notes: Optional[str] = None
    
    is_sealed: bool = False
    updated_at_utc: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReferralSummaryResponse(BaseModel):
    """Authoritative Presumptive Triage Summary for laboratory referral handoff."""
    session_id: str
    case_id: str
    event_id: Optional[str] = None
    operator_id: str
    field_officer_name: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None
    
    assay_profile_id: str
    assay_profile_version: str
    presumptive_outcome: Optional[str] = None
    decision_margin: Optional[float] = None
    
    evidence_id: Optional[str] = None
    evidence_digest: Optional[str] = None
    integrity_status: Optional[str] = None
    
    # Key Procedural References
    sample_identifier: Optional[str] = None
    seal_identifier: Optional[str] = None
    panchnama_memo_ref_no: Optional[str] = None
    kit_lot_number: Optional[str] = None
    
    # Triage Legal Disclaimer
    disclaimer: str = (
        "PRESUMPTIVE FIELD TRIAGE DATA ONLY. This record summarizes preliminary colorimetric "
        "field screening and procedural reference metadata. It does not constitute confirmatory "
        "chemical identification (GC-MS/HPLC) or judicial proof of guilt."
    )
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)
