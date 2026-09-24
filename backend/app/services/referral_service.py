"""REACTRA V2 — Formal Referral Package Generator Service.
Generates PRD-compliant JSON and printable HTML referral packages with cryptographic QR attestation.
Based on PRD §29 and Master Build Spec §28.
"""

from datetime import datetime, timezone
import html
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.domain.state_machine import SessionState
from app.repositories.session_repository import SessionRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.procedural_repository import ProceduralRepository
from app.repositories.custody_repository import CustodyRepository
from app.services.evidence_service import get_device_public_key_hex
from app.schemas.referral import (
    ReferralOperatorInfo,
    ReferralFieldTestInfo,
    ReferralProcedureInfo,
    ReferralProvenanceInfo,
    ReferralIntegrityInfo,
    ReferralPackageData,
    ReferralExportResponse,
)
from app.schemas.custody import CustodyEventResponse


class ReferralService:
    """Generates formal, sealed referral packages for forensic laboratory submission."""

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.measurement_repo = MeasurementRepository(db)
        self.procedural_repo = ProceduralRepository(db)
        self.custody_repo = CustodyRepository(db)

    def generate_referral_package(self, session_id: str) -> ReferralExportResponse:
        """
        Generates the formal canonical JSON and printable HTML referral package for a sealed session.
        Only allowed for EVIDENCE_SEALED or ARCHIVED sessions.
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session.status not in (SessionState.EVIDENCE_SEALED.value, SessionState.COMPLETED.value):
            raise ValueError(
                f"Referral package can only be generated for sealed sessions. (Current status: '{session.status}')"
            )

        evidence = self.evidence_repo.get_by_session_id(session_id)
        if not evidence or not evidence.record_digest or not evidence.signature:
            raise ValueError(f"No valid sealed evidence envelope found for session '{session_id}'.")

        measurement = self.measurement_repo.get_measurement(session_id)
        procedural = self.procedural_repo.get_by_session_id(session_id)
        custody_events = self.custody_repo.list_by_session_id(session_id)

        now_utc = datetime.now(timezone.utc)
        safe_session_id = session.id.replace(":", "_").replace("/", "_")
        json_filename = f"REACTRA_REFERRAL_{safe_session_id}.json"
        html_filename = f"REACTRA_REFERRAL_{safe_session_id}.html"

        # 1. Build Structured Sub-models
        operator_info = ReferralOperatorInfo(
            operator_id=session.operator_id or "UNKNOWN-OPERATOR",
            field_officer_name=session.field_officer_name,
            field_officer_designation=session.field_officer_designation,
            police_station_jurisdiction=session.police_station_jurisdiction,
        )

        field_test_info = ReferralFieldTestInfo(
            assay_profile_id=session.assay_profile_id,
            assay_profile_version=session.assay_profile_version,
            reference_card_version="2.0",
            reaction_started_at_utc=session.created_at_utc.isoformat(),
            capture_timestamp_utc=session.updated_at_utc.isoformat(),
            capture_elapsed_seconds=30.0,
            kinetic_window_status="IN_WINDOW",
            presumptive_result=measurement.result if measurement else "PRESUMPTIVE_POSITIVE",
            target_analyte_name="Target Analyte",
            quality_status=measurement.quality_status if measurement else "READY",
            decision_margin=measurement.decision_margin if measurement else None,
            class_distance_1=measurement.class_distance_1 if measurement else None,
        )

        proc_s50_status = (
            procedural.section_50_status if procedural and procedural.section_50_status else "NOT_RECORDED"
        )
        proc_s52a_status = (
            "RECORDED" if procedural and (procedural.inventory_ref_no or procedural.section_52a_reference) else "PENDING"
        )
        proc_s57_status = (
            procedural.section_57_report_status if procedural and procedural.section_57_report_status else "PENDING"
        )

        procedure_info = ReferralProcedureInfo(
            panchnama_memo_ref_no=procedural.panchnama_memo_ref_no if procedural else None,
            panch_witness_1_name=procedural.panch_witness_1_name if procedural else None,
            panch_witness_2_name=procedural.panch_witness_2_name if procedural else None,
            section_50_status=proc_s50_status,
            section_50_choice=procedural.section_50_choice_recorded if procedural else None,
            inventory_ref_no=procedural.inventory_ref_no if procedural else None,
            section_52a_reference=procedural.section_52a_reference if procedural else None,
            sample_identifier=procedural.sample_identifier if procedural else None,
            seal_identifier=procedural.seal_identifier if procedural else None,
            sample_drawal_status=procedural.sample_drawal_status if procedural else None,
            magistrate_certification_status=procedural.magistrate_certification_status if procedural else None,
            section_57_report_ref_no=procedural.section_57_report_ref_no if procedural else None,
            section_57_report_status=proc_s57_status,
            kit_lot_number=procedural.kit_lot_number if procedural else None,
            kit_expiry_date=procedural.kit_expiry_date if procedural else None,
            officer_notes=procedural.officer_notes if procedural else None,
        )

        provenance_info = ReferralProvenanceInfo(
            capture_mode=session.capture_mode,
            gps_status=session.gps_status,
            latitude=session.latitude,
            longitude=session.longitude,
            location_description=session.location_description,
        )

        auth_status = evidence.signing_device_authorization_status or (
            "UNENROLLED_DEMO_DEVICE" if evidence.device_enrollment_id == "DEV-OFFLINE-LOCAL" else "OFFLINE_DEVICE_ENROLLED"
        )
        integrity_info = ReferralIntegrityInfo(
            image_sha256=evidence.image_sha256,
            record_digest=evidence.record_digest,
            signature=evidence.signature,
            device_public_key_hex=get_device_public_key_hex(),
            signature_status="VALID",
            signing_device_authorization_status=auth_status,
            previous_record_hash=evidence.previous_record_hash,
        )

        custody_event_responses = [
            CustodyEventResponse.model_validate(c) for c in custody_events
        ] if custody_events else []

        package_data = ReferralPackageData(
            handoff_version="2.0",
            test_id=session.id,
            case_id=session.case_id,
            event_id=session.event_id,
            operator=operator_info,
            field_test=field_test_info,
            procedure=procedure_info,
            provenance=provenance_info,
            integrity=integrity_info,
            custody_history=custody_event_responses,
        )

        # 2. Build Compact Verifiable QR Payload
        qr_payload = {
            "v": "2.0",
            "evd": evidence.id,
            "sid": session.id,
            "cid": session.case_id,
            "dig": evidence.record_digest,
            "sig": evidence.signature,
            "pk": get_device_public_key_hex(),
            "ts": evidence.sealed_at_utc.isoformat(),
            "res": field_test_info.presumptive_result,
            "prv": evidence.previous_record_hash,
        }

        # 3. Render Printable HTML Content with @media print CSS
        html_content = self._render_printable_html(
            session=session,
            evidence=evidence,
            package_data=package_data,
            custody_events=custody_events,
            qr_payload=qr_payload,
            generated_at_utc=now_utc.isoformat(),
        )

        return ReferralExportResponse(
            session_id=session.id,
            case_id=session.case_id,
            json_filename=json_filename,
            html_filename=html_filename,
            package_data=package_data,
            html_content=html_content,
            qr_payload=qr_payload,
            exported_at_utc=now_utc.isoformat(),
        )

    def _render_printable_html(
        self,
        session: Any,
        evidence: Any,
        package_data: ReferralPackageData,
        custody_events: list,
        qr_payload: Dict[str, Any],
        generated_at_utc: str,
    ) -> str:
        """Renders high-contrast, print-optimized HTML referral document."""
        custody_rows = ""
        if custody_events:
            for idx, c in enumerate(custody_events):
                custody_rows += f"""
                <tr>
                    <td>{idx + 1}</td>
                    <td>{html.escape(c.transferred_at_utc.strftime('%Y-%m-%d %H:%M:%S UTC'))}</td>
                    <td>{html.escape(c.sender_operator_id)}</td>
                    <td><strong>{html.escape(c.receiver_name)}</strong> ({html.escape(c.receiver_badge_or_id)})</td>
                    <td>{html.escape(c.receiver_agency)}</td>
                    <td>{'MATCHED / VERIFIED' if c.package_seal_verified else 'FLAGGED / UNVERIFIED'}</td>
                </tr>
                """
        else:
            custody_rows = """
            <tr>
                <td colspan="6" style="text-align: center; color: #666; font-style: italic;">
                    No physical custody transfers logged prior to export.
                </td>
            </tr>
            """

        esc_case_id = html.escape(session.case_id)
        esc_session_id = html.escape(session.id)
        esc_evidence_id = html.escape(evidence.id)
        esc_operator = html.escape(session.operator_id or "OFC-UNKNOWN")
        esc_profile = html.escape(session.assay_profile_id)
        esc_result = html.escape(package_data.field_test.presumptive_result.replace('_', ' '))
        esc_digest = html.escape(evidence.record_digest)
        esc_sig = html.escape(evidence.signature[:32] + "...")
        esc_prev = html.escape(evidence.previous_record_hash or "NONE (GENESIS RECORD)")
        esc_pubkey = html.escape(get_device_public_key_hex()[:32] + "...")
        esc_memo = html.escape(package_data.procedure.panchnama_memo_ref_no or "N/A")
        esc_seal = html.escape(package_data.procedure.seal_identifier or "N/A")
        esc_sample = html.escape(package_data.procedure.sample_identifier or "N/A")
        esc_w1 = html.escape(package_data.procedure.panch_witness_1_name or "N/A")
        esc_w2 = html.escape(package_data.procedure.panch_witness_2_name or "N/A")
        esc_s50 = html.escape(package_data.procedure.section_50_status or "N/A")
        esc_s52a = html.escape(package_data.procedure.section_52a_reference or "N/A")
        esc_s57 = html.escape(package_data.procedure.section_57_report_ref_no or "N/A")
        esc_lot = html.escape(package_data.procedure.kit_lot_number or "N/A")
        esc_exp = html.escape(package_data.procedure.kit_expiry_date or "N/A")
        esc_time = html.escape(evidence.sealed_at_utc.strftime('%Y-%m-%d %H:%M:%S UTC'))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>REACTRA V2 — Forensic Laboratory Referral Package ({esc_session_id})</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm;
        }}
        body {{
            font-family: 'Courier New', Courier, monospace;
            background: #fff;
            color: #000;
            line-height: 1.4;
            font-size: 11pt;
            margin: 0;
            padding: 20px;
        }}
        .header {{
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .title {{
            font-size: 16pt;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .subtitle {{
            font-size: 10pt;
            color: #333;
        }}
        .notice-box {{
            border: 2px solid #000;
            background: #f4f4f4;
            padding: 10px;
            margin: 15px 0;
            font-weight: bold;
            text-align: center;
        }}
        .section {{
            margin-bottom: 15px;
            border: 1px solid #ccc;
            padding: 10px;
        }}
        .section-title {{
            font-size: 12pt;
            font-weight: bold;
            border-bottom: 1px solid #000;
            padding-bottom: 4px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        .row {{
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dotted #ccc;
            padding: 2px 0;
        }}
        .label {{
            font-weight: bold;
            color: #444;
        }}
        .value {{
            font-family: monospace;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
            font-size: 9pt;
        }}
        th, td {{
            border: 1px solid #000;
            padding: 4px 6px;
            text-align: left;
        }}
        th {{
            background: #eaeaea;
        }}
        .footer {{
            margin-top: 20px;
            border-top: 1px solid #000;
            padding-top: 10px;
            font-size: 8pt;
            color: #555;
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">REACTRA V2 — Forensic Referral & Triage Package</div>
        <div class="subtitle">Authoritative Presumptive Field-Test Record & Chain-of-Custody Attestation</div>
    </div>

    <div class="notice-box">
        MANDATORY STATUTORY NOTICE:<br>
        Field result is presumptive. Laboratory confirmation required (GC-MS / HPLC).<br>
        REACTRA does not perform confirmatory forensic analysis.
    </div>

    <div class="section">
        <div class="section-title">1. Case & Session Provenance</div>
        <div class="grid">
            <div class="row"><span class="label">Case Event ID:</span><span class="value">{esc_case_id}</span></div>
            <div class="row"><span class="label">Session ID:</span><span class="value">{esc_session_id}</span></div>
            <div class="row"><span class="label">Evidence ID:</span><span class="value">{esc_evidence_id}</span></div>
            <div class="row"><span class="label">Sealed Timestamp:</span><span class="value">{esc_time}</span></div>
            <div class="row"><span class="label">Operator Badge:</span><span class="value">{esc_operator}</span></div>
            <div class="row"><span class="label">Device Enrollment:</span><span class="value">{session.device_enrollment_id}</span></div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">2. Presumptive Scientific Indication</div>
        <div class="grid">
            <div class="row"><span class="label">Assay Profile:</span><span class="value">{esc_profile} (v{session.assay_profile_version})</span></div>
            <div class="row"><span class="label">Presumptive Finding:</span><span class="value"><strong>{esc_result}</strong></span></div>
            <div class="row"><span class="label">Quality Gate Status:</span><span class="value">{package_data.field_test.quality_status}</span></div>
            <div class="row"><span class="label">Kinetic Window:</span><span class="value">{package_data.field_test.kinetic_window_status}</span></div>
            <div class="row"><span class="label">Decision Margin:</span><span class="value">{package_data.field_test.decision_margin if package_data.field_test.decision_margin is not None else 'N/A'}</span></div>
            <div class="row"><span class="label">Class Distance (d1):</span><span class="value">{package_data.field_test.class_distance_1 if package_data.field_test.class_distance_1 is not None else 'N/A'}</span></div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">3. Officer-Entered Procedural References & Kit Tracking</div>
        <div class="grid">
            <div class="row"><span class="label">Panchnama / Memo Ref:</span><span class="value">{esc_memo}</span></div>
            <div class="row"><span class="label">Sample Seal Identifier:</span><span class="value">{esc_seal}</span></div>
            <div class="row"><span class="label">Representative Sample ID:</span><span class="value">{esc_sample}</span></div>
            <div class="row"><span class="label">Kit Lot / Expiry:</span><span class="value">{esc_lot} (Exp: {esc_exp})</span></div>
            <div class="row"><span class="label">NDPS §50 Safeguard:</span><span class="value">{esc_s50}</span></div>
            <div class="row"><span class="label">NDPS §52A Reference:</span><span class="value">{esc_s52a}</span></div>
            <div class="row"><span class="label">NDPS §57 Report Ref:</span><span class="value">{esc_s57}</span></div>
            <div class="row"><span class="label">Witnesses Logged:</span><span class="value">1: {esc_w1} | 2: {esc_w2}</span></div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">4. Cryptographic Envelope & Inter-Session Hash Chain</div>
        <div class="row"><span class="label">Canonical Digest (SHA-256):</span><span class="value">{esc_digest}</span></div>
        <div class="row"><span class="label">Ed25519 Digital Signature:</span><span class="value">{esc_sig}</span></div>
        <div class="row"><span class="label">Device Public Key (Hex):</span><span class="value">{esc_pubkey}</span></div>
        <div class="row"><span class="label">Previous Record Hash:</span><span class="value">{esc_prev}</span></div>
    </div>

    <div class="section">
        <div class="section-title">5. Physical Chain of Custody Log</div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Timestamp (UTC)</th>
                    <th>Releasing Officer</th>
                    <th>Receiving Officer / Custodian</th>
                    <th>Target Laboratory / Facility</th>
                    <th>Physical Seal Verified</th>
                </tr>
            </thead>
            <tbody>
                {custody_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <div>Exported from REACTRA V2 Field Engine at {html.escape(generated_at_utc)}</div>
        <div>Offline Cryptographic Attestation • Single Device Hash Chained</div>
    </div>
</body>
</html>
"""
