"""REACTRA V2 — Formal Referral Package Schemas (Pydantic V2).
Based on PRD Section 29 & Master Build Spec Section 28.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ConfigDict


class ReferralOperatorInfo(BaseModel):
    operator_id: str
    field_officer_name: Optional[str] = None
    field_officer_designation: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None


class ReferralFieldTestInfo(BaseModel):
    assay_profile_id: str
    assay_profile_version: str
    reference_card_version: str
    reaction_started_at_utc: Optional[str] = None
    capture_timestamp_utc: Optional[str] = None
    capture_elapsed_seconds: Optional[float] = None
    kinetic_window_status: str
    presumptive_result: str
    target_analyte_name: Optional[str] = None
    quality_status: str
    decision_margin: Optional[float] = None
    class_distance_1: Optional[float] = None


class ReferralProcedureInfo(BaseModel):
    panchnama_memo_ref_no: Optional[str] = None
    panch_witness_1_name: Optional[str] = None
    panch_witness_2_name: Optional[str] = None
    section_50_status: Optional[str] = None
    section_50_choice: Optional[str] = None
    inventory_ref_no: Optional[str] = None
    section_52a_reference: Optional[str] = None
    sample_identifier: Optional[str] = None
    seal_identifier: Optional[str] = None
    sample_drawal_status: Optional[str] = None
    magistrate_certification_status: Optional[str] = None
    section_57_report_ref_no: Optional[str] = None
    section_57_report_status: Optional[str] = None
    kit_lot_number: Optional[str] = None
    kit_expiry_date: Optional[str] = None
    officer_notes: Optional[str] = None


class ReferralProvenanceInfo(BaseModel):
    capture_mode: str
    gps_status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None


class ReferralIntegrityInfo(BaseModel):
    image_sha256: Optional[str] = None
    record_digest: str
    signature: str
    device_public_key_hex: str
    signature_status: str
    signing_device_authorization_status: str
    previous_record_hash: Optional[str] = None


from app.schemas.custody import CustodyEventResponse


class ReferralPackageData(BaseModel):
    handoff_version: str = "2.0"
    test_id: str
    case_id: str
    event_id: Optional[str] = None
    operator: ReferralOperatorInfo
    field_test: ReferralFieldTestInfo
    procedure: ReferralProcedureInfo
    provenance: ReferralProvenanceInfo
    integrity: ReferralIntegrityInfo
    notice: str = (
        "Field result is presumptive. Laboratory confirmation required (GC-MS / HPLC). "
        "REACTRA does not perform confirmatory forensic analysis."
    )
    mandatory_presumptive_notice: str = (
        "Field result is presumptive. Laboratory confirmation required (GC-MS / HPLC). "
        "REACTRA does not perform confirmatory forensic analysis."
    )
    custody_history: Optional[List[CustodyEventResponse]] = None


class ReferralExportResponse(BaseModel):
    session_id: str
    case_id: str
    json_filename: str
    html_filename: str
    package_data: ReferralPackageData
    html_content: str
    qr_payload: Dict[str, Any]
    exported_at_utc: str

    @property
    def referral_data(self) -> ReferralPackageData:
        return self.package_data

    @property
    def html_document(self) -> str:
        return self.html_content

    model_config = ConfigDict(from_attributes=True)
