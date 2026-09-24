export interface HealthResponse {
  status: string;
  service: string;
  api_version: string;
  app_version: string;
}

export interface ApiError {
  message: string;
  statusCode?: number;
  details?: unknown;
}

export interface AssayProfile {
  profile_id: string;
  name: string;
  reagent_name: string;
  profile_version: string;
  algorithm_version: string;
  reference_card_version: string;
  color_space: string;
  reagent_lot_required: boolean;
  is_active: boolean;
  description?: string;
}

export interface SessionCreateRequest {
  case_id: string;
  operator_id: string;
  device_enrollment_id?: string;
  is_demo_mode?: boolean;
  agency_id?: string;
  profile_id?: string;
  reference_card_id?: string;
  location_provenance?: string;
  notes?: string;
  assay_profile_id?: string;
  assay_profile_version?: string;
  capture_mode?: string;
  field_officer_name?: string;
  field_officer_designation?: string;
  police_station_jurisdiction?: string;
  gps_status?: string;
  location_description?: string;
  officer_notes?: string;
}

export interface SessionTransitionRequest {
  target_state: string;
  actor_id?: string;
  operator_id?: string;
  reason?: string;
  quality_passed?: boolean;
  event_payload?: Record<string, unknown>;
}

export interface AuditEventItem {
  event_id: string;
  test_id: string;
  event_type: string;
  from_state?: string;
  to_state?: string;
  actor_id: string;
  device_enrollment_id: string;
  event_payload?: Record<string, unknown>;
  event_timestamp_utc: string;
}

export interface ProceduralUpdateRequest {
  search_context_type?: string;
  panchnama_memo_ref_no?: string;
  witness_1_name?: string;
  witness_1_contact?: string;
  witness_2_name?: string;
  witness_2_contact?: string;
  section_50_applicable?: boolean;
  section_50_option_informed?: boolean;
  section_50_choice?: string;
  section_50_officer_name?: string;
  section_50_officer_designation?: string;
  section_52a_inventory_prepared?: boolean;
  section_52a_application_ref?: string;
  section_52a_magistrate_court?: string;
  sample_drawal_status?: string;
  magistrate_cert_status?: string;
  representative_sample_id?: string;
  sample_seal_identifier?: string;
  section_57_report_status?: string;
  section_57_report_ref?: string;
  section_57_submitted_to?: string;
  kit_lot_number?: string;
  kit_expiry_date?: string;
  officer_notes?: string;
}

export interface ProceduralContextResponse {
  id: number;
  test_id: string;
  search_context_type?: string;
  panchnama_memo_ref_no?: string;
  witness_1_name?: string;
  witness_1_contact?: string;
  witness_2_name?: string;
  witness_2_contact?: string;
  section_50_applicable?: boolean;
  section_50_option_informed?: boolean;
  section_50_choice?: string;
  section_50_officer_name?: string;
  section_50_officer_designation?: string;
  section_52a_inventory_prepared?: boolean;
  section_52a_application_ref?: string;
  section_52a_magistrate_court?: string;
  sample_drawal_status?: string;
  magistrate_cert_status?: string;
  representative_sample_id?: string;
  sample_seal_identifier?: string;
  section_57_report_status?: string;
  section_57_report_ref?: string;
  section_57_submitted_to?: string;
  kit_lot_number?: string;
  kit_expiry_date?: string;
  officer_notes?: string;
  created_at_utc?: string;
  updated_at_utc?: string;
}

export interface ReferralSummaryResponse {
  session_id: string;
  case_id: string;
  operator_id: string;
  agency_id?: string;
  assay_profile_id?: string;
  status: string;
  evidence_id?: string;
  presumptive_outcome?: string;
  target_analyte_name?: string;
  panchnama_memo_ref_no?: string;
  sample_seal_identifier?: string;
  representative_sample_id?: string;
  section_50_status?: string;
  section_52a_status?: string;
  section_57_status?: string;
  witnesses_recorded: number;
  kit_lot_number?: string;
  kit_expiry_date?: string;
  fsl_package_status: string;
  disclaimer: string;
}

export interface ReactionTimingItem {
  id: number;
  test_id: string;
  reaction_started_at_utc?: string;
  capture_timestamp_utc?: string;
  capture_elapsed_seconds?: number;
  timer_duration_seconds: number;
  timer_state: string;
  timing_flags?: Record<string, unknown>;
}

export interface CaptureRecordItem {
  id: string;
  session_id: string;
  provenance: string;
  image_path: string;
  image_sha256: string;
  quality_status: string;
  width?: number;
  height?: number;
  captured_at_utc: string;
}

export interface MeasurementResultItem {
  id: number;
  test_id: string;
  card_detection_confidence?: number;
  calibration_residual?: number;
  blur_metric?: number;
  exposure_metric?: number;
  glare_metric?: number;
  reaction_lab_l?: number;
  reaction_lab_a?: number;
  reaction_lab_b?: number;
  roi_pixel_count?: number;
  specular_rejected_pixel_count?: number;
  specular_rejected_fraction?: number;
  quality_status: string;
  result?: string;
  algorithm_version: string;
  model_version: string;
}

export interface EvidenceRecordItem {
  id: number;
  test_id: string;
  sealing_status: string;
  canonical_json_sha256?: string;
  envelope_signature?: string;
  signature_algorithm?: string;
  key_id?: string;
  sealed_at?: string;
}

export interface SessionDetailResponse {
  id: string;
  session_id?: string;
  case_id: string;
  event_id?: string;
  operator_id: string;
  field_officer_name?: string;
  field_officer_designation?: string;
  police_station_jurisdiction?: string;
  assay_profile_id: string;
  assay_profile_version: string;
  status: string;
  capture_mode: string;
  gps_status: string;
  latitude?: number;
  longitude?: number;
  location_accuracy?: number;
  location_description?: string;
  sync_state: string;
  device_enrollment_id: string;
  signing_key_fingerprint?: string;
  created_at_utc: string;
  updated_at_utc: string;
  timing?: ReactionTimingItem;
  measurement?: MeasurementResultItem;
  procedural_context?: ProceduralContextResponse;
  captures: CaptureRecordItem[];
  evidence?: EvidenceRecordItem;
  audit_events: AuditEventItem[];
}

export interface SessionSummaryResponse {
  id: string;
  case_id: string;
  operator_id: string;
  assay_profile_id: string;
  status: string;
  created_at_utc: string;
}

export interface SessionTimelineResponse {
  session_id: string;
  current_status: string;
  events: AuditEventItem[];
}

// Measurement & Adaptive Capture Guard Types (Phase 3)

export interface MeasurementExecuteRequest {
  image_base64: string;
  provenance?: string;
  elapsed_seconds?: number;
}

export interface BlurCheckData {
  variance: number;
  threshold: number;
  passed: boolean;
  explanation: string;
}

export interface ExposureCheckData {
  mean_luminance: number;
  underexposed_fraction: number;
  overexposed_fraction: number;
  dynamic_range: number;
  passed: boolean;
  explanation: string;
}

export interface GlareCheckData {
  max_roi_glare_fraction: number;
  threshold: number;
  passed: boolean;
  explanation: string;
  roi_glare_fractions: Record<string, number>;
}

export interface CardCheckData {
  detected: boolean;
  confidence: number;
  aspect_ratio: number;
  area_fraction: number;
  reason: string;
}

export interface AlignmentCheckData {
  passed: boolean;
  skew_angle_deg: number;
}

export interface CalibrationCheckData {
  passed: boolean;
  mean_delta_e: number;
  threshold: number;
  explanation: string;
  patch_count: number;
  patch_diagnostics: Record<string, unknown>;
}

export interface TimingCheckData {
  compliance_status: string;
  elapsed_seconds?: number;
  target_window_seconds: number;
  min_window_seconds: number;
  max_window_seconds: number;
  passed: boolean;
  explanation: string;
}

export interface QualityChecksGroupData {
  blur: BlurCheckData;
  exposure: ExposureCheckData;
  glare: GlareCheckData;
  card_detection: CardCheckData;
  alignment: AlignmentCheckData;
  calibration: CalibrationCheckData;
  timing: TimingCheckData;
}

export interface QualityDiagnosticsData {
  overall_status: string;
  passed_all_hard_gates: boolean;
  failure_reasons: string[];
  checks: QualityChecksGroupData;
}

export interface WellColorMeasurementData {
  roi_id: string;
  name: string;
  bbox: number[];
  sampled_bbox: number[];
  valid_pixel_count: number;
  glare_pixel_count: number;
  raw_lab_median: number[];
  calibrated_lab_median: number[];
  calibrated_lab_trimmed_mean: number[];
  lab_std_dev: number[];
  is_valid: boolean;
  rejection_reason?: string;
}

export interface ValidatedMeasurementData {
  measurement_id: string;
  session_id: string;
  capture_id: string;
  profile_id: string;
  profile_version: string;
  algorithm_version: string;
  reference_card_version: string;
  provenance: string;
  measured_at: string;
  timing_compliance: string;
  elapsed_seconds?: number;
  calibration_mean_delta_e: number;
  calibration_passed: boolean;
  well_measurements: Record<string, WellColorMeasurementData>;
  quality_diagnostics: QualityDiagnosticsData;
}

export interface MeasurementExecutionOutcomeData {
  session_id: string;
  session_status: string;
  passed_quality_gates: boolean;
  overall_quality_status: string;
  quality_diagnostics: QualityDiagnosticsData;
  validated_measurement?: ValidatedMeasurementData;
}

// Classifier & Explanation Types (Phase 4)

export interface ClassificationExplanationData {
  outcome?: string;
  outcome_state?: string;
  target_analyte_name?: string;
  reagent_name?: string;
  measured_lab?: [number, number, number] | number[];
  measured_lab_vector?: number[];
  target_centroid_lab?: [number, number, number] | number[];
  reference_centroid_lab?: number[];
  control_centroid_lab?: [number, number, number] | number[];
  negative_centroid_lab?: number[];
  distance_metric?: string;
  distance_to_target?: number;
  calculated_distance?: number;
  distance_to_control?: number;
  positive_threshold?: number;
  positive_boundary_threshold?: number;
  negative_threshold?: number;
  negative_boundary_threshold?: number;
  decision_margin?: number;
  profile_id?: string;
  assay_profile_id?: string;
  profile_version?: string;
  algorithm_version?: string;
  measurement_id?: string;
  timing_validity?: string;
  calibration_status?: string;
  quality_status?: string;
  threshold_status?: string;
  threshold_provenance?: string;
  presumptive_disclaimer?: string;
  scientific_disclaimer?: string;
  narrative_summary?: string;
}

export interface ClassificationResponse {
  session_id: string;
  session_status: string;
  outcome: string; // "PRESUMPTIVE_POSITIVE" | "PRESUMPTIVE_NEGATIVE" | "INCONCLUSIVE" | "INVALID_CAPTURE"
  class_distance_1: number;
  class_distance_2?: number;
  decision_margin: number;
  explanation: ClassificationExplanationData;
  threshold_status: string;
}

// Evidence Sealing & Verification Types (Phase 4)

export interface EvidenceSealResponse {
  session_id: string;
  evidence_id: string;
  canonical_record_json: string;
  record_digest: string;
  previous_record_hash?: string | null;
  signature: string;
  device_public_key_hex: string;
  device_enrollment_id: string;
  trust_registry_version: string;
  integrity_status: string;
  sealed_at_utc: string;
}

export interface EvidenceVerifyRequest {
  canonical_record_json: string;
  record_digest: string;
  signature: string;
  device_public_key_hex: string;
  device_enrollment_id?: string;
  trust_registry_version?: string;
}

export interface EvidenceVerifyResponse {
  verification_status: string; // "VERIFIED" | "TAMPER_DETECTED" | "INVALID_SIGNATURE" | "FORMAT_ERROR"
  canonical_digest_calculated: string;
  record_digest_claimed: string;
  digest_matches: boolean;
  signature_valid: boolean;
  device_public_key_hex: string;
  device_enrollment_id?: string;
  device_authorized: boolean;
  verified_at_utc: string;
  details: string;
}

// Phase 6 Types: Custody, Referral Package, Chain Verification

export interface CustodyCreateRequest {
  sender_operator_id: string;
  receiver_name: string;
  receiver_agency: string;
  receiver_badge_or_id: string;
  package_seal_verified: boolean;
  notes?: string;
}

export interface CustodyEventResponse {
  id: string;
  evidence_id: string;
  session_id: string;
  sender_operator_id: string;
  receiver_name: string;
  receiver_agency: string;
  receiver_badge_or_id: string;
  handoff_timestamp_utc: string;
  package_seal_verified: boolean;
  notes?: string;
  created_at_utc: string;
}

export interface ReferralPackageData {
  handoff_version: string;
  test_id: string;
  case_id: string;
  operator: {
    operator_id: string;
    field_officer_name?: string;
    field_officer_designation?: string;
    police_station_jurisdiction?: string;
  };
  field_test: {
    assay_profile_id: string;
    reagent_name?: string;
    target_analyte_name?: string;
    presumptive_outcome: string;
    decision_margin?: number;
    kit_lot_number?: string;
    kit_expiry_date?: string;
  };
  procedure: {
    search_context_type?: string;
    panchnama_memo_ref_no?: string;
    sample_seal_identifier?: string;
    representative_sample_id?: string;
    witness_1_name?: string;
    witness_2_name?: string;
    section_50_applicable?: boolean;
    section_52a_inventory_prepared?: boolean;
    section_57_report_status?: string;
  };
  provenance: {
    device_enrollment_id: string;
    gps_status?: string;
    location_description?: string;
    created_at_utc?: string;
    sealed_at_utc?: string;
  };
  integrity: {
    evidence_id: string;
    record_digest: string;
    previous_record_hash?: string | null;
    signature: string;
    device_public_key_hex: string;
    trust_registry_version: string;
  };
  mandatory_presumptive_notice: string;
  custody_history?: CustodyEventResponse[];
}

export interface ReferralExportResponse {
  test_id: string;
  session_id: string;
  json_filename: string;
  html_filename: string;
  referral_data: ReferralPackageData;
  html_document: string;
  qr_payload: Record<string, string>;
  export_timestamp_utc: string;
}

export interface ChainVerificationItem {
  sequence_index: number;
  session_id: string;
  evidence_id: string;
  record_digest: string;
  previous_record_hash?: string | null;
  signature_valid: boolean;
  digest_valid: boolean;
  chain_link_valid: boolean;
  sealed_at_utc: string;
  error_detail?: string;
}

export interface ChainVerificationResponse {
  chain_status: "CHAIN_VALID" | "CHAIN_DISCONTINUITY" | "RECORD_ORDER_VIOLATION" | "EMPTY_CHAIN";
  device_enrollment_id: string;
  total_records: number;
  records: ChainVerificationItem[];
  verified_at_utc: string;
  explanation: string;
}


