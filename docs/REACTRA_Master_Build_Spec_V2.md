# REACTRA — MASTER BUILD SPECIFICATION V2
# Digital Companion for Field Drug Testing
# SIH 2026 — Problem Statement SIH26231
# Version: 2.0
# Date: 22 September 2026
#
# PROJECT IDENTITY
# REACTRA = Reaction-Aware Field Testing & Verifiable Evidence
#
# IMPORTANT:
# This document supersedes the previous REACTRA prototype specification wherever
# the two documents conflict. Preserve already-working modules when they comply
# with this V2 contract. Do not remove working cryptography, calibration,
# quality-gate, local database, or evidence functions merely to redesign the UI.
#
# PRIMARY PRODUCT POSITIONING
# REACTRA is NOT an "AI drug detector".
# REACTRA is a field evidence companion that helps a trained operator:
#   1. capture a colorimetric field-test result under controlled imaging conditions,
#   2. determine whether the captured measurement is usable,
#   3. obtain an explainable presumptive interpretation for the configured test profile,
#   4. preserve the event as a tamper-evident digital record,
#   5. maintain a searchable evidence timeline,
#   6. prepare a structured laboratory handoff.
#
# The result is PRESUMPTIVE only. Laboratory confirmation remains required.
#
# ---------------------------------------------------------------------------
# 00 — CHANGE CONTROL: WHAT IS NEW IN V2
# ---------------------------------------------------------------------------
#
# V2 incorporates the following product-level changes that were not sufficiently
# represented in the earlier prototype specification:
#
# V2-01. Replace "AI scanner" positioning with "Field Evidence Intelligence Layer".
# V2-02. Model the complete Indian field workflow: encounter/search -> recovery ->
#       presumptive field test -> documentation -> seizure/sample handling ->
#       laboratory confirmation -> investigation/case workflow.
# V2-03. Explicitly separate:
#       A. Measurement Validity
#       B. Presumptive Classification
#       C. Evidence Integrity
#       D. Legal/Case Status (which REACTRA does NOT decide).
# V2-04. Add a FIRST-CLASS INVALID CAPTURE outcome in addition to
#       POSITIVE / NEGATIVE / INCONCLUSIVE.
# V2-05. Add an Adaptive Capture Guard: REACTRA must reject poor images before
#       classification and tell the operator exactly how to improve the capture.
# V2-06. Add lighting-aware capture guidance for night use, glare, exposure,
#       blur, and reference-card framing.
# V2-07. Add explicit "test-profile" architecture so results never use a generic
#       one-size-fits-all colour model across unrelated kits.
# V2-08. Add profile version, algorithm version, reference-card version,
#       camera/capture metadata, and provenance metadata to evidence records.
# V2-09. Add an Evidence Integrity view that is clearly distinct from a
#       classification confidence score.
# V2-10. Add a complete Evidence Timeline / Chain-of-Events view.
# V2-11. Add a Laboratory Handoff workflow for presumptive/ambiguous cases.
# V2-12. Add "unknown/unmatched profile" handling: never force a classification.
# V2-13. Add "legal status is separate from chemical presumptive result" UX.
# V2-14. Add offline-first field operation and explicit network/sync status.
# V2-15. Improve differentiation versus commercial products such as DetectaChem
#       MobileDetect: do NOT claim camera scanning, GPS, reporting, or local
#       storage are unique; differentiate through measurement gating,
#       explainability, integrity architecture, profile/version provenance,
#       and evidence lifecycle design.
# V2-16. Add judge-facing demo scenarios that show failure prevention, not only
#       successful classification.
# V2-17. Replace outdated reference to Indian Evidence Act Section 65B with
#       current Bharatiya Sakshya Adhiniyam terminology. REACTRA must not claim
#       legal admissibility merely because it uses cryptography.
# V2-18. Keep synthetic benchmark data, but make every metric visibly labelled
#       "controlled synthetic prototype benchmark — not field accuracy".
#
# ---------------------------------------------------------------------------
# 01 — AUTHORITATIVE PROBLEM DEFINITION
# ---------------------------------------------------------------------------
#
# SIH26231 asks for a mobile/web application that works alongside existing
# colorimetric field-test kits, without new hardware. The statement specifically
# calls for:
#
#   - image capture of the test result,
#   - a reference colour card in-frame for lighting calibration,
#   - automatic classification into defined outcomes such as positive,
#     negative, and inconclusive,
#   - a tamper-evident record including timestamp, GPS, operator identifier,
#     and a cryptographic image hash,
#   - a simple searchable log,
#   - a signed digital record,
#   - and an explicit understanding that the output is presumptive and does not
#     replace laboratory confirmation.
#
# REACTRA therefore must solve TWO connected problems:
#
# PROBLEM A — MEASUREMENT STANDARDISATION
#   Reduce subjectivity in visual interpretation of a colour-change reaction.
#
# PROBLEM B — DIGITAL TRACEABILITY
#   Turn a momentary field observation into a structured, verifiable,
#   tamper-evident event that can be searched and handed forward in the case
#   lifecycle.
#
# The product must never expand these into:
#   "REACTRA proves the substance is an illicit drug."
#   "REACTRA determines guilt."
#   "REACTRA determines whether possession is legal."
#
# ---------------------------------------------------------------------------
# 02 — REAL-WORLD FIELD WORKFLOW IN INDIA: PRODUCT MODEL
# ---------------------------------------------------------------------------
#
# IMPORTANT PRODUCT CONTEXT
#
# The exact legal procedure varies with the circumstances and applicable powers,
# but the operational chain relevant to REACTRA is broadly:
#
#   encounter / intelligence / checkpoint event
#             |
#             v
#   lawful interception/search/recovery
#             |
#             v
#   suspected material identified for further examination
#             |
#             v
#   presumptive field-test procedure using an approved/configured kit
#             |
#             v
#   reaction observed and documented
#             |
#             v
#   presumptive field result recorded
#             |
#             v
#   seizure / sampling / sealing / documentation as required by procedure
#             |
#             v
#   forensic laboratory confirmation
#             |
#             v
#   investigation / case record / judicial process
#
# REACTRA begins where the approved field-test procedure begins and continues
# into the evidence-documentation and laboratory-handoff layer.
#
# REACTRA MUST NOT automate or replace:
#   - statutory search/arrest decisions,
#   - assessment of legal possession,
#   - statutory safeguards,
#   - seizure authority,
#   - sampling/sealing acts that must follow departmental procedure,
#   - laboratory identification,
#   - prosecutorial decisions,
#   - or judicial findings.
#
# ---------------------------------------------------------------------------
# 03 — THE "MEDICINE VS ILLICIT SUBSTANCE" DISTINCTION
# ---------------------------------------------------------------------------
#
# A key product principle:
#
#   "A presumptive chemical reaction" != "a legal finding of unlawful possession".
#
# A person may possess a pharmaceutical/medical product under lawful conditions.
# Appearance alone is not a reliable chemical identity method, and chemical identity
# does not by itself answer every legal question surrounding possession.
#
# REACTRA must therefore present:
#
#   SUBSTANCE TEST RESULT
#       |
#       +--> Presumptive field-test interpretation
#
# separately from:
#
#   CASE / LEGAL CONTEXT
#       |
#       +--> Officer-entered notes / documentation fields
#       +--> Authorization/documentation status where applicable
#       +--> "Not determined by REACTRA"
#
# The UI wording must NEVER imply:
#
#   POSITIVE = GUILTY
#   POSITIVE = ILLEGAL POSSESSION
#   NEGATIVE = NOTHING ILLEGAL
#
# Preferred wording:
#
#   "PRESUMPTIVE POSITIVE FOR THE CONFIGURED TEST PROFILE"
#   "PRESUMPTIVE NEGATIVE FOR THE CONFIGURED TEST PROFILE"
#   "INCONCLUSIVE — REVIEW / LABORATORY CONFIRMATION REQUIRED"
#   "INVALID CAPTURE — NO CLASSIFICATION GENERATED"
#
# ---------------------------------------------------------------------------
# 04 — PRIMARY END USERS
# ---------------------------------------------------------------------------
#
# PRIMARY USER
#   Trained field officer / drug-law-enforcement officer / designated screener.
#
# SECONDARY USERS
#   Supervisor reviewing field-test records.
#   Forensic/laboratory staff receiving a referral packet.
#   Evidence/audit personnel verifying integrity.
#
# PRODUCT DESIGN PRINCIPLE
#   The field operator is under time pressure.
#   The UI must therefore minimize typing and choices during capture.
#   The operator should be guided by the application, not forced to interpret
#   developer/debug information.
#
# ---------------------------------------------------------------------------
# 05 — CORE PRODUCT PRINCIPLE: THREE SCORES, NOT ONE
# ---------------------------------------------------------------------------
#
# REACTRA must NEVER collapse the entire decision into one arbitrary number such
# as "95% accurate" or "95% drug confidence".
#
# Use three conceptually separate dimensions:
#
# 1. MEASUREMENT VALIDITY
#    "Was the image physically usable for analysis?"
#    Inputs: blur, exposure, glare, card geometry, ROI integrity,
#            calibration residual, framing.
#
# 2. PRESUMPTIVE CLASSIFICATION
#    "Given a valid calibrated image and a configured assay profile, which
#     defined outcome category is closest?"
#    Inputs: calibrated colour features, class centroids/distance metrics,
#            decision margins.
#
# 3. EVIDENCE INTEGRITY
#    "Has the digital record remained cryptographically consistent with the
#     captured image and signed content?"
#    Inputs: SHA-256, canonical serialization, Ed25519 signature,
#            backward-linking audit chain, verification result.
#
# A fourth area is intentionally NOT an AI score:
#
# 4. CASE / LEGAL STATUS
#    "What legal conclusion applies?"
#    This is outside REACTRA's automated authority.
#
# ---------------------------------------------------------------------------
# 06 — PRODUCT DIFFERENTIATION STRATEGY
# ---------------------------------------------------------------------------
#
# MARKET REALITY
#
# Commercial products already demonstrate that smartphone-based presumptive test
# analysis can:
#   - scan a test,
#   - automate interpretation,
#   - create reports,
#   - capture time/date,
#   - capture GPS,
#   - store results locally,
#   - and support multiple tests.
#
# Therefore REACTRA MUST NOT claim:
#   "We are the first app to use a smartphone camera."
#   "We invented mobile drug-test reporting."
#   "GPS reporting is unique."
#   "A mobile app itself is novel."
#
# DIFFERENTIATION PILLARS
#
# PILLAR 1 — MEASUREMENT VALIDITY BEFORE CLASSIFICATION
#   REACTRA refuses to classify unusable captures.
#
# PILLAR 2 — ADAPTIVE CAPTURE GUARD
#   The camera workflow actively explains why a retake is needed:
#      "Too dark"
#      "Reference card not detected"
#      "Excessive glare"
#      "Hold device steadier"
#      "Reaction ROI not visible"
#   This is an operator-assistance layer, not just a post-hoc classifier.
#
# PILLAR 3 — EXPLAINABLE PRESUMPTIVE INTERPRETATION
#   Show which profile was used, how the colour was calibrated, the measured
#   colour, class distances, and decision margin.
#
# PILLAR 4 — FOUR-STATE OUTCOME MODEL
#   POSITIVE / NEGATIVE / INCONCLUSIVE / INVALID CAPTURE.
#   "Invalid" is a measurement problem, not a chemical conclusion.
#
# PILLAR 5 — EVIDENCE RELIABILITY PASSPORT
#   One structured audit view combining Capture, Measurement,
#   Classification and Evidence Integrity.
#
# PILLAR 6 — CRYPTOGRAPHIC PROVENANCE
#   Image hash + canonical record hash + Ed25519 signature +
#   backward-linking local audit chain.
#
# PILLAR 7 — VERSION-AWARE ASSAY PROFILES
#   Every result is bound to the exact assay profile version, reference-card
#   version, algorithm version and model version used at the time.
#
# PILLAR 8 — EVIDENCE TIMELINE
#   REACTRA shows the sequence of events instead of only producing a report.
#
# PILLAR 9 — LABORATORY HANDOFF
#   The output is designed to accompany, not replace, laboratory confirmation.
#
# PILLAR 10 — INDIA-CONTEXT FIELD WORKFLOW
#   The product is explicitly structured around Indian narcotics field screening,
#   documentation and laboratory handoff concepts rather than being a generic
#   consumer "drug scanner".
#
# PILLAR 11 — OFFLINE-FIRST, HONEST METADATA
#   No fake GPS. No fake device metadata. No hidden cloud dependency.
#
# PILLAR 12 — OPERATOR DECISION SUPPORT, NOT AUTONOMOUS ENFORCEMENT
#   The product makes uncertainty visible and lets trained personnel follow
#   department SOPs.
#
# ---------------------------------------------------------------------------
# 07 — REACTRA END-TO-END OPERATOR FLOW
# ---------------------------------------------------------------------------
#
# HERO FLOW:
#
#   [1 SETUP]
#       |
#       v
#   [2 CAPTURE]
#       |
#       v
#   [3 CHECK]
#       |
#       +---- FAIL ----> [RECAPTURE / REVIEW]
#       |
#       v
#   [4 ANALYZE]
#       |
#       v
#   [5 RESULT]
#       |
#       v
#   [6 EVIDENCE]
#       |
#       v
#   [7 COMPLETE / LAB HANDOFF]
#
# Note:
# The previous six-step model is retained conceptually, but V2 makes
# ANALYSIS/RESULT and LAB HANDOFF explicit so the operator clearly sees what
# happened and where the presumptive result ends.
#
# ---------------------------------------------------------------------------
# 08 — STEP 1: SETUP SCREEN
# ---------------------------------------------------------------------------
#
# SCREEN TITLE:
#   "START FIELD TEST"
#
# Required fields:
#
#   Test Session ID
#       Auto-generated UUID.
#
#   Operator ID
#       Required.
#
#   Case / Event ID
#       Optional in demo; strongly recommended for production.
#
#   Kit / Assay Profile
#       Select only an approved configured profile.
#
#   Kit Lot / Batch
#       Optional for MVP, P1 recommended.
#
#   Kit Expiry / Validity
#       Optional in MVP, P1 recommended.
#
#   Capture Mode
#       LIVE_CAMERA
#       IMPORTED_IMAGE (only for QA/demo workflows)
#
#   Location Status
#       GPS_DEVICE
#       UNAVAILABLE
#       MANUAL_DEMO (demo only, never represented as device GPS)
#
# Guardrails:
#   - Never silently populate fake coordinates.
#   - Never silently substitute one assay profile for another.
#   - If profile is uncalibrated or unsupported, block analysis.
#
# ---------------------------------------------------------------------------
# 09 — STEP 2: ADAPTIVE CAPTURE GUARD
# ---------------------------------------------------------------------------
#
# THIS IS A MAJOR V2 DIFFERENTIATOR.
#
# The camera is not just an upload box. It is a measurement-quality assistant.
#
# Before capture:
#   - show reference-card framing outline,
#   - show reaction-zone framing guide,
#   - show guidance for glare,
#   - show low-light warning,
#   - keep UI readable at night,
#   - minimize operator actions.
#
# DURING CAPTURE / IMMEDIATE ANALYSIS:
#
#   A. Is the reference card visible?
#   B. Are required fiducials visible?
#   C. Is the image sufficiently sharp?
#   D. Is exposure inside usable bounds?
#   E. Is specular glare too large?
#   F. Is the reaction region visible and large enough?
#   G. Is perspective correction possible?
#   H. Is the correct assay profile identifiable?
#
# If a hard condition fails:
#   DO NOT CLASSIFY.
#
# Instead show:
#
#   "CAPTURE INVALID"
#   "Reason: Reference card not detected."
#   "Action: Include the complete reference card and retake."
#
# OR
#
#   "CAPTURE INVALID"
#   "Reason: Excessive glare."
#   "Action: Change angle / lighting and retake."
#
# OR
#
#   "CAPTURE INVALID"
#   "Reason: Motion blur."
#   "Action: Hold device steady and retake."
#
# SOFT REVIEW conditions may show:
#   "REVIEW REQUIRED"
#   but must still prevent a conclusive automated interpretation if the
#   measurement validity policy requires classification to stop.
#
# ---------------------------------------------------------------------------
# 10 — STEP 3: MEASUREMENT CHECK
# ---------------------------------------------------------------------------
#
# PIPELINE INVARIANT:
#
#   CAPTURE
#      ->
#   QUALITY GATE
#      ->
#       FAIL = STOP / NO CLASSIFIER
#      ->
#       PASS
#      ->
#   CARD LOCALIZATION
#      ->
#   PERSPECTIVE WARP
#      ->
#   CALIBRATION
#      ->
#   ROI EXTRACTION
#      ->
#   CLASSIFICATION
#
# NOTE:
# The previous prototype contained a temporary violation where some REVIEW
# states could still reach classification. V2 requires an explicit safety
# gate in the service layer, not only in the UI.
#
# REQUIRED QUALITY METRICS
#
#   Blur:
#       Laplacian variance threshold configured by profile/device.
#
#   Exposure:
#       Mean luminance / usable dynamic-range check.
#
#   Glare:
#       Saturated/high-specular pixel fraction.
#
#   Card:
#       Card geometry / fiducial confidence.
#
#   Calibration:
#       Mean calibration residual (e.g., Delta E76) within profile threshold.
#
#   ROI:
#       Reaction zone visible and sufficiently populated.
#
# IMPORTANT:
# Thresholds in the prototype are engineering parameters, not validated
# forensic/legal standards unless experimentally established for the exact
# camera, card, kit, reagent and environment.
#
# ---------------------------------------------------------------------------
# 11 — FOUR OUTCOME STATES
# ---------------------------------------------------------------------------
#
# STATE A — PRESUMPTIVE POSITIVE
#   The valid calibrated capture falls within the configured positive region.
#
# STATE B — PRESUMPTIVE NEGATIVE
#   The valid calibrated capture falls within the configured negative region
#   for the configured assay/protocol.
#
# STATE C — INCONCLUSIVE
#   The result lies near class boundaries, the reaction appears ambiguous,
#   or the configured assay does not support a confident classification.
#
# STATE D — INVALID CAPTURE
#   The image failed the measurement-quality gate.
#
# IMPORTANT DIFFERENCE:
#   INCONCLUSIVE = measurement may be valid, but the classification is not clear.
#   INVALID CAPTURE = the image itself is not acceptable for interpretation.
#
# The classifier must never output a result for INVALID CAPTURE.
#
# ---------------------------------------------------------------------------
# 12 — STEP 4: CARD LOCALIZATION & PERSPECTIVE NORMALIZATION
# ---------------------------------------------------------------------------
#
# The reference card is a calibration reference, not decoration.
#
# Functions:
#   - detect QR / profile marker where available,
#   - detect four-corner fiducials,
#   - estimate card quadrilateral,
#   - reject severe occlusion,
#   - perspective-warp to canonical geometry,
#   - sample reference patches,
#   - record card-detection metrics.
#
# Preferred data:
#   card_profile_id
#   card_profile_version
#   card_detection_confidence
#   perspective_transform_status
#   reference_patch_count
#
# ---------------------------------------------------------------------------
# 13 — STEP 5: ILLUMINATION / COLOUR CALIBRATION
# ---------------------------------------------------------------------------
#
# REQUIRED CONCEPT:
#
#   Raw camera colour
#       ->
#   reference-card observation
#       ->
#   colour/illumination correction
#       ->
#   calibrated colour
#       ->
#   classification
#
# Reference implementation:
#   CIE L*a*b* representation
#   Least-squares affine transformation
#   Delta E76 residual measurement
#
# Keep the existing mathematics from the previous prototype where it is tested.
#
# BUT:
# Never claim that this simple affine model solves every physical lighting,
# sensor, lens, spectral or chemical variation. It compensates within the limits
# demonstrated by the calibrated reference and benchmark.
#
# ---------------------------------------------------------------------------
# 14 — STEP 6: REACTION REGION OF INTEREST
# ---------------------------------------------------------------------------
#
# The system must distinguish:
#
#   reference patches
#   reaction ROI
#   pouch/container boundaries
#   background
#   glare/reflections
#
# Save the ROI geometry used in the evidence record.
#
# UI:
#   overlay reaction ROI
#   show reference patch boundaries
#   show analysis region on a zoomed crop
#
# This creates explainability:
#   "This is the region REACTRA actually measured."
#
# ---------------------------------------------------------------------------
# 15 — STEP 7: KIT / ASSAY PROFILE ENGINE
# ---------------------------------------------------------------------------
#
# REACTRA must be profile-driven.
#
# Example profile object:
#
#   profile_id
#   profile_name
#   profile_version
#   manufacturer_or_source (if applicable)
#   reference_card_version
#   supported_outcomes
#   calibration_targets
#   positive_features / centroid(s)
#   negative_features / centroid(s)
#   inconclusive_margin
#   quality thresholds
#   safety notes
#   profile_status
#
# REQUIRED PROFILE STATES:
#
#   CALIBRATED
#   DEMO_ONLY
#   STAGED
#   DISABLED
#
# If a real kit profile lacks validated physical calibration data:
#   - do not present it as operational,
#   - mark it STAGED / DEMO_ONLY,
#   - show warning,
#   - block production-style classification.
#
# Do not invent chemical centroids for real narcotics.
#
# ---------------------------------------------------------------------------
# 16 — STEP 8: EXPLAINABLE PRESUMPTIVE CLASSIFIER
# ---------------------------------------------------------------------------
#
# Retain the prototype's nearest-centroid concept where suitable:
#
#   distance = DeltaE(calibrated_reaction, class_centroid)
#
# Then evaluate:
#   nearest class
#   runner-up class
#   separation margin
#
# Output:
#   class
#   measured colour
#   nearest class distance
#   second-nearest distance
#   margin
#   decision rule
#   profile version
#
# REQUIRED RULE:
#
#   If the classification margin is insufficient:
#       -> INCONCLUSIVE
#
# Never force:
#   POSITIVE
#   NEGATIVE
#
# simply because one class is marginally closer.
#
# UI MUST NOT say:
#   "98.2% chance this is cocaine"
#
# UI MAY say:
#   "Presumptive Positive — configured profile"
#   "Decision margin: 18.4 Delta E"
#   "Classification generated from calibrated colour distance"
#
# ---------------------------------------------------------------------------
# 17 — UNKNOWN / UNMATCHED TEST HANDLING
# ---------------------------------------------------------------------------
#
# Scenario:
#   The operator has a result or sample that does not correspond to a configured
#   assay profile.
#
# REACTRA response:
#
#   "NO MATCHING ASSAY PROFILE"
#   "REACTRA cannot produce a presumptive classification for this configuration."
#   "Record captured for review."
#   "Laboratory confirmation / appropriate SOP required."
#
# The app must not guess the drug identity from generic image appearance.
#
# ---------------------------------------------------------------------------
# 18 — EXPIRY / DEGRADED REAGENT HANDLING
# ---------------------------------------------------------------------------
#
# Expired, damaged or contaminated test materials can produce abnormal, weak,
# delayed or otherwise difficult-to-interpret colour responses.
#
# MVP handling:
#   - allow operator to record kit lot/expiry when available,
#   - flag expired/unknown kit state,
#   - use inconclusive/review logic,
#   - prevent false confidence,
#   - recommend laboratory confirmation where required.
#
# Future:
#   temporal reaction analysis may examine reaction trajectories, but it is
#   NOT part of the validated MVP and must remain a research feature.
#
# ---------------------------------------------------------------------------
# 19 — STEP 9: RESULT SCREEN
# ---------------------------------------------------------------------------
#
# RESULT SCREEN MUST HAVE A STRONG HIERARCHY.
#
# TOP:
#   PRESUMPTIVE FIELD-TEST RESULT
#   Laboratory confirmation is required.
#
# CENTER:
#   PRESUMPTIVE POSITIVE
#   OR
#   PRESUMPTIVE NEGATIVE
#   OR
#   INCONCLUSIVE — REVIEW
#   OR
#   INVALID CAPTURE — RETAKE
#
# UNDER RESULT:
#   Profile: <id> v<version>
#   Measurement status: READY / REVIEW / INVALID
#   Classification explanation:
#       measured colour
#       nearest reference
#       decision margin
#
# VISUAL EXPLANATION:
#   original image
#   corrected image
#   card boundary
#   reference patches
#   reaction ROI
#   optional colour swatch comparison
#
# ---------------------------------------------------------------------------
# 20 — STEP 10: EVIDENCE RELIABILITY PASSPORT
# ---------------------------------------------------------------------------
#
# This is a flagship REACTRA feature.
#
# Every completed field test receives a 4-part Reliability Passport:
#
# SECTION A — CAPTURE
#   test_id
#   timestamp
#   operator_id
#   capture_mode
#   location source
#   device/camera metadata where reliably available
#   original image digest
#
# SECTION B — MEASUREMENT
#   card detected
#   card profile/version
#   calibration method
#   calibration residual
#   blur metric
#   exposure metric
#   glare metric
#   ROI status
#   quality gate status
#
# SECTION C — CLASSIFICATION
#   configured profile
#   profile version
#   result
#   class distances
#   decision margin
#   model/algorithm version
#   "presumptive" label
#
# SECTION D — EVIDENCE INTEGRITY
#   image SHA-256
#   canonical record digest
#   Ed25519 signature status
#   public key fingerprint
#   previous record hash
#   chain verification state
#
# BADGES:
#
#   READY
#       Measurement valid + presumptive result generated + evidence sealed.
#
#   REVIEW
#       Ambiguous/soft quality condition and/or inconclusive result.
#
#   RECAPTURE
#       Hard measurement failure; classification blocked.
#
#   REFERRAL REQUIRED
#       Case/test should move toward laboratory examination according to SOP.
#
# Do not use "court admissible" as a UI badge.
#
# ---------------------------------------------------------------------------
# 21 — EVIDENCE INTEGRITY IS NOT CLASSIFICATION CONFIDENCE
# ---------------------------------------------------------------------------
#
# The UI must visually separate:
#
#   "CLASSIFICATION"
#       What did the calibrated test result resemble?
#
# from:
#
#   "EVIDENCE INTEGRITY"
#       Can we verify that this digital record remains internally consistent?
#
# Example:
#
#   Classification:
#       PRESUMPTIVE POSITIVE
#
#   Evidence Integrity:
#       VERIFIED
#
# The second does NOT make the first chemically confirmed.
#
# Conversely:
#
#   Classification:
#       INCONCLUSIVE
#   Evidence Integrity:
#       VERIFIED
#
# is entirely valid: the record can be perfectly trustworthy while the chemical
# interpretation remains inconclusive.
#
# ---------------------------------------------------------------------------
# 22 — CRYPTOGRAPHIC EVIDENCE ENVELOPE
# ---------------------------------------------------------------------------
#
# Retain the existing successful architecture:
#
#   SHA-256
#   canonical JSON serialization
#   Ed25519 signatures
#   backward-linking hash chain
#   SQLite local persistence
#
# Canonicalization:
#   json-sort-keys-compact-utf8-v1
#
# Preimage must contain all material analytical metadata.
#
# Cryptographic fields excluded from preimage:
#   record_digest
#   signature
#   public_key_fingerprint
#
# Evidence record should include:
#
#   evidence_format_version
#   test_id
#   timestamp_utc
#   operator_id
#   case_id
#   capture_mode
#   gps_status
#   latitude
#   longitude
#   location_accuracy where genuinely available
#   assay_profile_id
#   assay_profile_version
#   reference_card_version
#   algorithm_version
#   model_version
#   quality_gate_status
#   measurement_quality
#   result
#   classification metrics
#   image_sha256
#   previous_record_hash
#
# Envelope adds:
#   record_digest
#   signature
#   public_key_fingerprint
#   canonical_algorithm
#
# ---------------------------------------------------------------------------
# 23 — AUDIT HASH CHAIN
# ---------------------------------------------------------------------------
#
# Each record points backward:
#
#   Record 0
#      previous_record_hash = null
#
#   Record 1
#      previous_record_hash = digest(Record 0)
#
#   Record 2
#      previous_record_hash = digest(Record 1)
#
#   ...
#
# Verification checks:
#   1. canonical digest matches content,
#   2. signature matches digest,
#   3. previous link matches preceding record,
#   4. chain order is intact.
#
# Expected alerts:
#   "DIGEST MISMATCH"
#   "SIGNATURE INVALID"
#   "CHAIN DISCONTINUITY"
#   "RECORD ORDER VIOLATION"
#
# IMPORTANT:
# A local hash chain is tamper-evident within its trust model; it is not magical
# protection against an already-compromised operating system/device.
#
# ---------------------------------------------------------------------------
# 24 — IMAGE PROVENANCE AND CAPTURE MODE
# ---------------------------------------------------------------------------
#
# Every image must be labelled:
#
#   LIVE_CAMERA
#   IMPORTED_IMAGE
#
# IMPORTED_IMAGE is a QA/demo path and must remain visibly marked.
#
# REACTRA must never present an imported image as if it were a contemporaneous
# live field capture.
#
# Image provenance record:
#   capture_mode
#   ingestion_timestamp
#   image_sha256
#   image_dimensions
#   source label
#   optional device metadata when available
#
# ---------------------------------------------------------------------------
# 25 — LOCATION HANDLING
# ---------------------------------------------------------------------------
#
# Location states:
#
#   GPS_DEVICE
#       Genuine device-provided coordinates.
#
#   UNAVAILABLE
#       Device/browser did not supply trusted coordinates.
#
#   MANUAL_DEMO
#       Explicit hackathon/demo-only coordinate entry.
#
# NEVER:
#   silently use IP geolocation,
#   fabricate coordinates,
#   label manual coordinates as GPS,
#   imply high precision unsupported by the device.
#
# Production roadmap:
#   native Android/iOS location bridge
#   accuracy field
#   permission state
#   capture time binding
#
# ---------------------------------------------------------------------------
# 26 — OFFLINE-FIRST FIELD ARCHITECTURE
# ---------------------------------------------------------------------------
#
# CORE OPERATION MUST WORK WITHOUT INTERNET:
#
#   capture
#   quality gate
#   calibration
#   classification for configured profile
#   evidence hashing
#   digital signature
#   local storage
#   history search
#   integrity verification
#   export
#
# NETWORK IS OPTIONAL FOR:
#   synchronization
#   supervisory upload
#   central case integration
#   laboratory gateway integration
#
# SYNC STATE:
#   LOCAL_ONLY
#   PENDING_SYNC
#   SYNCED
#   SYNC_FAILED
#
# The UI must never imply that a record is centrally received merely because it
# exists on the device.
#
# ---------------------------------------------------------------------------
# 27 — EVIDENCE TIMELINE
# ---------------------------------------------------------------------------
#
# Each test should expose a chronological timeline such as:
#
#   23:38:11  Session created
#   23:39:02  Operator authenticated
#   23:40:21  Capture initiated
#   23:40:24  Image accepted
#   23:40:25  Quality gate passed
#   23:40:26  Calibration completed
#   23:40:27  Presumptive interpretation generated
#   23:40:29  Officer reviewed result
#   23:40:34  Evidence record signed
#   23:40:35  Local chain committed
#   00:12:18  Record exported / queued for sync
#
# This is a reconstruction aid, not a substitute for underlying official logs.
#
# ---------------------------------------------------------------------------
# 28 — LABORATORY HANDOFF
# ---------------------------------------------------------------------------
#
# REACTRA's role:
#   make the field test record easy to carry forward.
#
# Create:
#
#   RECTRA_REFERRAL_<test_id>.json
#   RECTRA_REFERRAL_<test_id>.html
#
# Packet should contain:
#   test/case identifiers
#   operator
#   timestamps
#   location provenance
#   assay profile/version
#   field presumptive result
#   quality metrics
#   original image digest
#   evidence record digest
#   signature status
#   chain link
#   sample/evidence identifiers entered by operator
#   explicit note:
#       "Field result is presumptive. Laboratory confirmation required."
#
# Do NOT generate:
#   a fake GC-MS report,
#   a fake FSL result,
#   a fake chemical identification certificate.
#
# ---------------------------------------------------------------------------
# 29 — SEARCHABLE HISTORY
# ---------------------------------------------------------------------------
#
# Minimum filters:
#   Test ID
#   Case ID
#   Operator
#   Date/time range
#   Result
#   Measurement status
#   Integrity status
#   Assay profile
#   Sync state
#
# Search result card:
#   test id
#   date/time
#   operator
#   result
#   status badge
#   profile
#   evidence integrity
#
# Open record:
#   full Reliability Passport
#   evidence timeline
#   original/corrected image
#   cryptographic verification
#   referral/export actions
#
# ---------------------------------------------------------------------------
# 30 — UI / UX DESIGN SPECIFICATION
# ---------------------------------------------------------------------------
#
# FIELD MODE
#   Large controls.
#   Minimal text entry.
#   High contrast.
#   Night-readable.
#   One primary action per screen.
#
# TOP STATUS BAR:
#   Operator
#   Test ID
#   Assay profile
#   GPS status
#   Offline/Sync status
#
# MAIN NAVIGATION:
#
#   NEW TEST
#   ACTIVE TEST
#   HISTORY
#   EVIDENCE VERIFY
#
# SECONDARY / DEVELOPER:
#   VALIDATION / QA MODE
#   BENCHMARKS
#   TAMPER DEMOS
#   DEBUG LOGS
#
# FIELD MODE MUST NOT expose:
#   stack traces,
#   SQL errors,
#   raw numpy arrays,
#   developer-only metrics as the main user experience.
#
# ---------------------------------------------------------------------------
# 31 — UX COPY RULES
# ---------------------------------------------------------------------------
#
# GOOD:
#   "Presumptive Positive"
#   "Reference Card Detected"
#   "Calibration Passed"
#   "Capture Invalid — Retake Required"
#   "Inconclusive — Laboratory Review Recommended"
#   "Evidence Integrity Verified"
#
# BAD:
#   "100% Drug Detected"
#   "Guilty"
#   "Definitely Cocaine"
#   "Court-Proven"
#   "AI Certainty 99.99%"
#
# Avoid the phrase:
#   "confidence = chemical truth"
#
# ---------------------------------------------------------------------------
# 32 — TECHNICAL ARCHITECTURE
# ---------------------------------------------------------------------------
#
# Recommended modular structure:
#
#   reactra/
#     ui/
#       pages/
#       components/
#       field_mode/
#       qa_mode/
#
#     session/
#       state_machine.py
#       manager.py
#       recovery.py
#
#     vision/
#       capture.py
#       card_detector.py
#       calibration.py
#       quality_gate.py
#       roi_detector.py
#       exposure.py
#       glare.py
#
#     profiles/
#       loader.py
#       validator.py
#       schemas/
#       profiles/
#
#     classification/
#       predictor.py
#       thresholds.py
#       evaluation.py
#
#     evidence/
#       canonical.py
#       hashing.py
#       signing.py
#       chain.py
#       verifier.py
#       envelope.py
#       timeline.py
#
#     database/
#       connection.py
#       schema.py
#       repository.py
#       migrations.py
#
#     referral/
#       lab_packet.py
#
#     metadata/
#       location.py
#       device.py
#
#     security/
#       key_store.py
#       access.py
#
#     demo/
#       scenarios.py
#       fixtures.py
#
#   app.py
#
# UI / SERVICE SEPARATION RULE:
#   UI may display data.
#   UI must not own scientific algorithms, SQL, or cryptographic primitives.
#
# ---------------------------------------------------------------------------
# 33 — SESSION STATE MACHINE
# ---------------------------------------------------------------------------
#
# Required states:
#
#   DRAFT
#   CAPTURED
#   QUALITY_CHECKING
#   VALIDATION_FAILED
#   READY_FOR_CLASSIFICATION
#   CLASSIFIED
#   REVIEW_REQUIRED
#   REFERRAL_REQUIRED
#   EVIDENCE_SEALED
#   COMPLETED
#
# Example transitions:
#
#   DRAFT
#      -> CAPTURED
#      -> QUALITY_CHECKING
#
#   QUALITY_CHECKING
#      -> VALIDATION_FAILED
#      -> READY_FOR_CLASSIFICATION
#
#   VALIDATION_FAILED
#      -> CAPTURED
#
#   READY_FOR_CLASSIFICATION
#      -> CLASSIFIED
#      -> REVIEW_REQUIRED
#
#   CLASSIFIED
#      -> EVIDENCE_SEALED
#
#   REVIEW_REQUIRED
#      -> REFERRAL_REQUIRED
#      -> EVIDENCE_SEALED
#
#   EVIDENCE_SEALED
#      -> COMPLETED
#
# Persistence requirement:
#   active session must survive navigation and application refresh where
#   technically supported.
#
# ---------------------------------------------------------------------------
# 34 — SAFETY / FORENSIC GUARDRAILS
# ---------------------------------------------------------------------------
#
# REACTRA is a decision-support tool, not an autonomous enforcement system.
#
# NEVER:
#   - make arrest recommendations,
#   - determine guilt,
#   - determine legal possession,
#   - invent a drug identity for an unsupported profile,
#   - replace laboratory confirmation,
#   - fabricate GPS,
#   - fabricate test records,
#   - silently edit sealed evidence,
#   - report synthetic benchmarks as field accuracy.
#
# ALWAYS:
#   - label presumptive results,
#   - show profile/version,
#   - show measurement status,
#   - show evidence integrity separately,
#   - preserve original image hash,
#   - preserve provenance,
#   - allow verification,
#   - expose uncertainty.
#
# ---------------------------------------------------------------------------
# 35 — DIGITAL EVIDENCE / CURRENT INDIAN LAW TERMINOLOGY
# ---------------------------------------------------------------------------
#
# The previous specification referenced "Section 65B of the Indian Evidence Act".
# V2 must update that language for current deployments.
#
# The Bharatiya Sakshya Adhiniyam, 2023 is the current central evidence statute
# and came into force on 1 July 2024. Its electronic-record provisions include
# conditions and certificate requirements for electronic evidence in proceedings.
#
# REACTRA must therefore use cautious wording:
#
#   "Designed to preserve integrity and provenance of electronic records."
#
# NOT:
#
#   "Cryptography makes this automatically legally admissible."
#
# Any production deployment should be reviewed against the then-current legal,
# departmental, forensic and procedural requirements.
#
# ---------------------------------------------------------------------------
# 36 — DATA MODEL
# ---------------------------------------------------------------------------
#
# TABLE: test_sessions
#   id
#   case_id
#   operator_id
#   assay_profile_id
#   assay_profile_version
#   status
#   capture_mode
#   created_at_utc
#   updated_at_utc
#   gps_status
#   latitude
#   longitude
#   location_accuracy
#   sync_state
#
# TABLE: evidence_records
#   test_id
#   image_path / secure image reference
#   image_sha256
#   canonical_record_json
#   record_digest
#   signature
#   public_key_fingerprint
#   previous_record_hash
#   integrity_status
#
# TABLE: measurement_results
#   test_id
#   card_detection_confidence
#   calibration_residual
#   blur_metric
#   exposure_metric
#   glare_metric
#   roi_pixel_count
#   quality_status
#   result
#   class_distance_1
#   class_distance_2
#   decision_margin
#
# TABLE: assay_profiles
#   profile_id
#   profile_version
#   status
#   reference_card_version
#   threshold_configuration
#   calibration_targets
#   classifier_configuration
#
# TABLE: audit_events
#   event_id
#   test_id
#   event_type
#   event_timestamp_utc
#   event_payload_hash
#   previous_event_hash
#
# ---------------------------------------------------------------------------
# 37 — SECURITY THREAT MODEL V2
# ---------------------------------------------------------------------------
#
# T1 IMAGE TAMPERING
#   Defense: SHA-256 hash committed to signed evidence record.
#
# T2 RESULT TAMPERING
#   Defense: canonical record + Ed25519 signature.
#
# T3 METRIC TAMPERING
#   Defense: metrics included in signed preimage.
#
# T4 RECORD DELETION
#   Defense: backward-linking hash chain + exported envelopes.
#
# T5 RECORD REORDERING
#   Defense: chain verification.
#
# T6 PROFILE VERSION REINTERPRETATION
#   Defense: profile_version/reference_card_version/algorithm_version frozen
#           into evidence record.
#
# T7 IMPORTED IMAGE MISREPRESENTED AS LIVE
#   Defense: capture_mode immutable in evidence record and visible in UI.
#
# T8 GPS FABRICATION
#   Defense: explicit gps_status and provenance.
#
# T9 POOR IMAGE CAUSING BAD RESULT
#   Defense: quality gate before classifier.
#
# T10 UNMATCHED ASSAY
#   Defense: no profile -> no classification.
#
# T11 PRIVATE KEY COMPROMISE
#   MVP: OS-restricted key storage.
#   Production: Android Keystore / iOS Secure Enclave / TPM/HSM where available.
#
# T12 DEVICE COMPROMISE
#   Trust-boundary limitation: cryptography cannot prove the camera sensor
#   itself was truthful before capture.
#
# ---------------------------------------------------------------------------
# 38 — TECHNICAL LIMITATIONS TO DISPLAY IN DOCUMENTATION
# ---------------------------------------------------------------------------
#
# 1. Field tests are presumptive.
# 2. The prototype benchmark is synthetic.
# 3. Affine CIE Lab calibration has limits.
# 4. Camera sensor differences require real-device validation.
# 5. Physical assay chemistry and reagent aging cannot be fully simulated by
#    colour centroids alone.
# 6. Cross-reactivity/adulteration cannot be solved merely by a generic colour
#    classifier.
# 7. An unknown substance outside the configured assay profile cannot be safely
#    identified by REACTRA's generic image pipeline.
# 8. GPS availability depends on OS/device permissions.
# 9. Cryptographic integrity is not equivalent to legal admissibility.
# 10. Production thresholds must be validated using real authorised test-kit
#     data and departmental SOPs.
#
# ---------------------------------------------------------------------------
# 39 — SYNTHETIC DATA / ETHICAL PROTOTYPING POLICY
# ---------------------------------------------------------------------------
#
# REACTRA should use synthetic images for the hackathon prototype.
#
# Synthetic benchmark may model:
#   - known colour centroids,
#   - perspective changes,
#   - blur,
#   - exposure,
#   - glare,
#   - card misalignment,
#   - ambiguous mid-point colours.
#
# Do NOT state:
#   "REACTRA is 100% accurate in the real world."
#
# State:
#   "REACTRA achieved X on a controlled synthetic benchmark with known ground
#    truth. This does not estimate field performance."
#
# A future physical validation programme requires:
#   appropriate institutional approvals,
#   authorised materials,
#   controlled laboratory/forensic supervision,
#   documented sampling and calibration,
#   and a defensible dataset.
#
# ---------------------------------------------------------------------------
# 40 — BENCHMARK METRICS
# ---------------------------------------------------------------------------
#
# Existing synthetic benchmark may continue to report:
#   POSITIVE support = 5
#   NEGATIVE support = 5
#   INCONCLUSIVE support = 5
#   controlled synthetic macro precision/recall/F1
#
# But every result screen and presentation slide must label these:
#
#   "CONTROLLED SYNTHETIC PROTOTYPE BENCHMARK"
#
# Physical quality-gate tests:
#   motion blur -> expected RECAPTURE
#   severe glare -> expected RECAPTURE
#   missing card -> expected RECAPTURE
#   failed calibration -> expected REVIEW / RECAPTURE
#
# The key engineering acceptance test is:
#
#   "No hard-fail image reaches the classifier."
#
# ---------------------------------------------------------------------------
# 41 — REQUIRED DEMO SCENARIOS
# ---------------------------------------------------------------------------
#
# DEMO 1 — GOOD CAPTURE
#   Result:
#      quality gate passed
#      classification generated
#      evidence sealed
#
# DEMO 2 — NIGHT / LOW LIGHT
#   Show:
#      poor exposure warning
#      operator guidance
#      retake
#      successful calibrated capture
#
# DEMO 3 — GLARE
#   Show:
#      glare detection
#      classification blocked
#      retake instruction
#
# DEMO 4 — MOTION BLUR
#   Show:
#      blur metric
#      RECAPTURE REQUIRED
#      classifier invocation count = 0
#
# DEMO 5 — AMBIGUOUS REACTION
#   Show:
#      valid measurement
#      INCONCLUSIVE
#      REVIEW
#      lab referral generated
#
# DEMO 6 — UNKNOWN PROFILE
#   Show:
#      no matching assay
#      no forced identity
#      referral/review path
#
# DEMO 7 — TAMPERED RECORD
#   Edit:
#      result OR operator OR metric
#   Verify:
#      digest/signature failure
#
# DEMO 8 — DELETED RECORD
#   Delete:
#      intermediate chain record
#   Verify:
#      chain discontinuity
#
# DEMO 9 — IMPORTED IMAGE
#   Show:
#      clearly labelled IMPORTED_IMAGE
#
# DEMO 10 — GPS UNAVAILABLE
#   Show:
#      "GPS: UNAVAILABLE"
#
# DEMO 11 — OFFLINE MODE
#   Disable network.
#   Complete:
#      capture -> analysis -> seal -> search.
#
# DEMO 12 — EVIDENCE TIMELINE
#   Show:
#      ordered chain-of-events with integrity status.
#
# ---------------------------------------------------------------------------
# 42 — PRIMARY 4-MINUTE JUDGE DEMO
# ---------------------------------------------------------------------------
#
# 0:00-0:25
#   Frame the problem:
#   "The existing field kit gives a colour reaction. The human interpretation
#    and documentation around that reaction are where subjectivity and
#    traceability become problems."
#
# 0:25-0:55
#   Show:
#      START FIELD TEST
#      operator
#      assay profile
#      location status
#
# 0:55-1:35
#   Show:
#      night/poor capture
#      Adaptive Capture Guard
#      invalid capture
#      retake instruction
#
# 1:35-2:05
#   Show:
#      reference card detected
#      calibration
#      quality gate
#      ROI overlay
#
# 2:05-2:35
#   Show:
#      presumptive result
#      explanation panel
#      explicit laboratory-confirmation banner
#
# 2:35-3:10
#   Show:
#      Reliability Passport
#      Evidence Integrity: VERIFIED
#      hash/signature/chain
#
# 3:10-3:35
#   Show:
#      tamper one field in exported JSON
#      verification failure
#
# 3:35-4:00
#   Show:
#      evidence timeline
#      laboratory referral packet
#
# FINAL LINE:
#   "REACTRA does not replace the field kit or the forensic laboratory.
#    It makes the field measurement more standardized, the uncertainty visible,
#    and the digital record verifiable."
#
# ---------------------------------------------------------------------------
# 43 — JUDGE Q&A: CORE ANSWERS
# ---------------------------------------------------------------------------
#
# Q: "Does this already exist?"
# A:
#   "Mobile presumptive-test products already exist, so we are not claiming
#   smartphone scanning itself as novel. Our focus is the combination of
#   pre-classification measurement gating, explainable calibrated colour analysis,
#   four-state outcomes, versioned assay provenance, cryptographic evidence
#   integrity, and an end-to-end field-to-laboratory record."
#
# Q: "How are you different from DetectaChem MobileDetect?"
# A:
#   "DetectaChem demonstrates automated field-test analysis and reporting, so we
#   do not claim those basic capabilities as unique. REACTRA's differentiation is
#   its explicit measurement-validity gate, operator-guided recapture workflow,
#   transparent calibration/classification explanation, versioned evidence
#   provenance, locally verifiable cryptographic chain, and India-context
#   evidence/laboratory workflow model."
#
# Q: "Why not deep learning?"
# A:
#   "We need measurement transparency and controlled behaviour more than a
#   black-box identity claim. A colour-distance model in calibrated space is easy
#   to inspect, test, threshold, and explain. A neural model can be considered
#   later only after a sufficiently validated physical dataset exists."
#
# Q: "What if lighting is terrible?"
# A:
#   "REACTRA does not guess. The reference card is used for calibration and the
#   Adaptive Capture Guard checks blur, exposure, glare, card geometry and ROI.
#   A hard failure blocks classification."
#
# Q: "What if the result is ambiguous?"
# A:
#   "INCONCLUSIVE. We do not force a positive or negative classification."
#
# Q: "What if the kit is not supported?"
# A:
#   "No matching profile means no automated classification. The event can still
#   be documented and referred."
#
# Q: "Does a positive result prove illegal possession?"
# A:
#   "No. It is a presumptive field-test result for the configured assay. Legal
#   status and final chemical identification are outside the app's authority."
#
# Q: "Does a negative result prove no NDPS substance is present?"
# A:
#   "No. The configured field kit has a defined scope; a negative result only
#   means the configured test did not produce the relevant presumptive indication."
#
# Q: "Does the hash make it court-admissible?"
# A:
#   "No automatic guarantee. It strengthens integrity and provenance. Legal
#   admissibility remains subject to applicable law, procedure, certification,
#   evidence rules and judicial assessment."
#
# Q: "Why offline?"
# A:
#   "The field measurement must not depend on cellular availability. The
#   computational and evidence-preservation pipeline therefore runs locally,
#   while synchronization is optional."
#
# Q: "Why not blockchain?"
# A:
#   "For a single offline field device, a local backward-linking signed record
#   chain gives an auditable integrity mechanism without requiring network
#   consensus."
#
# Q: "Why synthetic data?"
# A:
#   "For safety, legality and reproducibility. The prototype can demonstrate
#   algorithmic behaviour without handling controlled substances. Real-world
#   deployment requires authorised validation data."
#
# ---------------------------------------------------------------------------
# 44 — CURRENT TECH STACK RECOMMENDATION
# ---------------------------------------------------------------------------
#
# MVP:
#   Language: Python 3.11
#   UI: Streamlit for functional prototype
#   CV: OpenCV + NumPy + Pillow
#   QR: OpenCV QRCodeDetector where supported
#   Database: SQLite
#   Crypto: cryptography package
#   Packaging: local files / JSON / HTML
#
# P1:
#   Native Android/iOS camera + GPS bridge
#   OS-backed secure key storage
#
# P2:
#   Kinetic video experiments
#   per-device camera profiling
#   controlled physical validation
#
# P3:
#   institutional/LIMS/evidence-system integration only through authorised
#   interfaces and approved deployments.
#
# ---------------------------------------------------------------------------
# 45 — PREVIOUS PROTOTYPE: COMPONENTS TO PRESERVE
# ---------------------------------------------------------------------------
#
# Preserve working:
#   - CIE Lab calibration implementation
#   - reference-card detection
#   - perspective transform
#   - quality gate logic
#   - nearest-centroid classifier
#   - inconclusive margin logic
#   - SQLite repository
#   - canonical JSON
#   - SHA-256 hashing
#   - Ed25519 signing/verification
#   - local hash chain
#   - evidence envelope export
#   - laboratory referral generator
#   - synthetic benchmark generator
#   - automated tests
#
# Fix before demo:
#   - legacy RECTRA/REACTRA naming inconsistency
#   - classifier execution on hard/invalid quality failures
#   - session loss across navigation/refresh
#   - generic "NONE" status strings
#   - fake/default location presentation
#   - developer console mixed with operator UX
#
# ---------------------------------------------------------------------------
# 46 — FILE / CODE IMPLEMENTATION CONTRACT
# ---------------------------------------------------------------------------
#
# REQUIRED:
#
#   app.py
#      starts application
#
#   src/reactra/session/
#      state machine and recovery
#
#   src/reactra/vision/
#      all CV and measurement validation
#
#   src/reactra/profiles/
#      profile loading and validation
#
#   src/reactra/classification/
#      classifier and evaluation
#
#   src/reactra/evidence/
#      canonicalization, hashing, signing, chain, verification
#
#   src/reactra/database/
#      SQLite persistence
#
#   src/reactra/referral/
#      lab packet generation
#
#   tests/unit/
#   tests/integration/
#
# ---------------------------------------------------------------------------
# 47 — ACCEPTANCE CRITERIA V2
# ---------------------------------------------------------------------------
#
# FUNCTIONAL
#   [ ] Start Field Test works
#   [ ] Operator ID required
#   [ ] Profile must be selected
#   [ ] Capture mode recorded
#   [ ] Location status explicit
#   [ ] Live capture works
#   [ ] Imported-image QA path works
#   [ ] Reference card detected
#   [ ] Perspective normalization works
#   [ ] Quality gate works
#   [ ] Hard quality failure blocks classifier
#   [ ] Retake instructions shown
#   [ ] Calibration works
#   [ ] ROI detected
#   [ ] POSITIVE works on synthetic benchmark
#   [ ] NEGATIVE works on synthetic benchmark
#   [ ] INCONCLUSIVE works
#   [ ] INVALID CAPTURE works
#   [ ] Unknown profile is rejected
#
# EVIDENCE
#   [ ] Timestamp stored
#   [ ] Operator stored
#   [ ] Location provenance stored
#   [ ] Image SHA-256 generated
#   [ ] Canonical record generated
#   [ ] Ed25519 signature generated
#   [ ] Signature verifies
#   [ ] Hash chain links
#   [ ] Chain verifies
#   [ ] Tampering is detected
#   [ ] Imported image remains labelled
#   [ ] Evidence timeline visible
#
# LAB HANDOFF
#   [ ] Referral packet generated for inconclusive/review/referral condition
#   [ ] Presumptive disclaimer included
#   [ ] No fake laboratory result generated
#
# UX
#   [ ] Field mode is simple
#   [ ] QA mode separated
#   [ ] Night-readable interface
#   [ ] Actionable capture messages
#   [ ] Classification and evidence integrity visually separated
#
# HONESTY
#   [ ] No fake GPS
#   [ ] No fake field accuracy
#   [ ] No unsupported drug-identification claims
#   [ ] No legal/admissibility guarantee
#
# ---------------------------------------------------------------------------
# 48 — REQUIRED TESTS
# ---------------------------------------------------------------------------
#
# Unit tests:
#   calibration
#   canonicalization
#   hashing
#   signing
#   chain
#   profile loader
#   classifier
#   quality gate
#   ROI
#   referral packet
#   session state machine
#
# Integration tests:
#   end-to-end positive
#   end-to-end negative
#   end-to-end inconclusive
#   blur hard-block
#   glare hard-block
#   missing-card hard-block
#   failed-calibration block
#   unknown-profile block
#   tampered-result detection
#   tampered-image detection
#   deleted-chain-link detection
#   reordered-chain detection
#   imported-image provenance
#   GPS unavailable
#   manual demo location
#   offline workflow
#
# CRITICAL SAFETY ASSERTION:
#
#   if quality_gate_status == INVALID/RECAPTURE:
#       classifier must not execute
#       classification must remain null
#
# ---------------------------------------------------------------------------
# 49 — PERFORMANCE REPORTING RULES
# ---------------------------------------------------------------------------
#
# Allowed:
#   "On 17 controlled synthetic images, the prototype correctly exercised the
#    configured quality-gate scenarios."
#
# Allowed:
#   "Synthetic benchmark macro F1 = 1.00 on 15 constructed examples."
#
# Not allowed:
#   "REACTRA has 100% real-world accuracy."
#
# Not allowed:
#   "REACTRA can identify every illegal drug."
#
# Not allowed:
#   "REACTRA is scientifically proven for field deployment."
#
# Performance metrics must include:
#   dataset composition
#   synthetic/real status
#   support count
#   profile
#   camera/device conditions
#   known limitations
#
# ---------------------------------------------------------------------------
# 50 — ROADMAP
# ---------------------------------------------------------------------------
#
# PHASE 0 — HACKATHON MVP
#   - Streamlit field workflow
#   - reference card
#   - calibration
#   - quality gate
#   - four-state outcome model
#   - explainable classifier
#   - Reliability Passport
#   - signed evidence envelope
#   - local chain
#   - search
#   - lab referral packet
#   - deterministic synthetic demos
#
# PHASE 1 — FIELD HARDENING
#   - native mobile camera
#   - real device GPS
#   - secure hardware-backed keys
#   - device-specific camera profiling
#   - role-based authentication
#   - kit lot / expiry metadata
#   - multilingual field UI
#   - controlled user testing with authorised personnel
#
# PHASE 2 — RESEARCH
#   - reaction video / DeltaE(t)
#   - temporal consistency checks
#   - more sophisticated optical processing
#   - controlled physical assay dataset
#
# PHASE 3 — INSTITUTIONAL INTEGRATION
#   - approved laboratory/LIMS integration
#   - approved evidence-system integration
#   - central audit/sync
#   - supervisor dashboards
#
# ---------------------------------------------------------------------------
# 51 — UI SCREEN INVENTORY
# ---------------------------------------------------------------------------
#
# 01 SPLASH / AUTH
#   REACTRA
#   Operator authentication
#
# 02 HOME
#   START FIELD TEST
#   CONTINUE ACTIVE TEST
#   HISTORY
#   VERIFY EVIDENCE
#   SETTINGS
#
# 03 SETUP
#   Operator / case / profile / location status
#
# 04 CAPTURE
#   Camera
#   reference card outline
#   reaction ROI guide
#   adaptive warnings
#
# 05 CHECK
#   blur
#   exposure
#   glare
#   card
#   calibration
#   ROI
#   overall readiness
#
# 06 ANALYSIS
#   corrected image
#   reference patches
#   reaction ROI
#   colour-space view
#
# 07 RESULT
#   presumptive result
#   inconclusive / invalid handling
#   explanation
#   lab confirmation banner
#
# 08 EVIDENCE PASSPORT
#   four sections
#   sign & seal
#
# 09 TIMELINE
#   ordered events
#
# 10 EXPORT / LAB REFERRAL
#
# 11 HISTORY
#
# 12 VERIFY EVIDENCE
#   digest
#   signature
#   chain
#
# 13 QA / DEMO MODE
#   synthetic scenarios
#   benchmark
#   tamper demo
#
# ---------------------------------------------------------------------------
# 52 — VISUAL DESIGN LANGUAGE
# ---------------------------------------------------------------------------
#
# The interface should feel like a serious field instrument, not a consumer
# social app.
#
# Desired characteristics:
#   clear
#   calm
#   high contrast
#   sparse
#   evidence-oriented
#   readable outdoors/at night
#   obvious system state
#   obvious uncertainty
#
# Avoid:
#   excessive animations
#   gamification
#   huge "AI magic" illustrations
#   fake glowing confidence meters
#   ambiguous colours as the only status signal
#
# Every status should use:
#   icon + text + state.
#
# Example:
#   [✓] REFERENCE CARD DETECTED
#   [✓] MEASUREMENT READY
#   [!] INCONCLUSIVE
#   [✕] CAPTURE INVALID
#
# ---------------------------------------------------------------------------
# 53 — MASTER PRODUCT MESSAGE
# ---------------------------------------------------------------------------
#
# ONE-LINE:
#   "REACTRA turns a subjective field colour test into a standardized,
#    explainable and verifiable digital evidence event."
#
# TWO-LINE:
#   "We do not replace the kit or laboratory. We improve the layer in between:
#    measurement quality, presumptive interpretation, operator guidance and
#    evidence provenance."
#
# THREE-PART STORY:
#
#   MEASURE
#      Standardize the visual observation.
#
#   EXPLAIN
#      Show why the result was generated or withheld.
#
#   PRESERVE
#      Seal the event into a verifiable digital record.
#
# ---------------------------------------------------------------------------
# 54 — IMPLEMENTATION PRIORITY ORDER
# ---------------------------------------------------------------------------
#
# MUST HAVE FOR NEXT PROTOTYPE BUILD:
#
#   1. REACTRA branding everywhere.
#   2. New field-user UX.
#   3. Adaptive Capture Guard.
#   4. Four outcome states.
#   5. Strict classifier blocking on hard measurement failure.
#   6. Profile-driven configuration.
#   7. Reliability Passport.
#   8. Evidence Timeline.
#   9. Cryptographic verification screen.
#   10. Lab Referral Packet.
#
# SHOULD HAVE:
#   11. Offline indicator.
#   12. GPS provenance indicator.
#   13. Case/Event ID.
#   14. Kit lot/expiry fields.
#   15. Unknown-profile workflow.
#   16. multilingual-ready UI.
#
# FUTURE:
#   17. Native camera/GPS.
#   18. Hardware-backed keys.
#   19. Temporal reaction analysis.
#   20. authorised physical validation.
#
# ---------------------------------------------------------------------------
# 55 — ANTI-PATTERN CHECKLIST
# ---------------------------------------------------------------------------
#
# DO NOT BUILD:
#
#   [ ] "Upload photo -> chatbot -> drug name"
#   [ ] single "AI confidence" score
#   [ ] classifier that accepts blurry/overexposed images
#   [ ] generic classifier with no kit profile
#   [ ] positive/negative only
#   [ ] fake GPS
#   [ ] fake laboratory certificate
#   [ ] cloud required for core operation
#   [ ] blockchain solely for marketing
#   [ ] unsupported claims of forensic certification
#   [ ] hard-coded result hidden behind "AI"
#
# ---------------------------------------------------------------------------
# 56 — READY-TO-USE MASTER BUILD PROMPT FOR ANTIGRAVITY/CODING AGENT
# ---------------------------------------------------------------------------
#
# Use the following as the implementation contract for the next coding pass.
#
# BEGIN MASTER BUILD PROMPT
#
# You are rebuilding the existing REACTRA prototype for SIH26231.
#
# Preserve all working scientific and cryptographic modules unless explicitly
# incompatible with this V2 specification.
#
# Product identity:
#   REACTRA — Reaction-Aware Field Testing & Verifiable Evidence.
#
# Mission:
#   Build an offline-first field companion for colorimetric presumptive drug
#   testing that standardizes image-based interpretation, rejects poor
#   measurements, explains the result, preserves provenance, and prepares a
#   laboratory handoff.
#
# NON-NEGOTIABLE PRINCIPLES:
#   1. REACTRA is not a chemical confirmation system.
#   2. REACTRA does not determine legal possession or guilt.
#   3. Presumptive result is always labelled presumptive.
#   4. Laboratory confirmation is required.
#   5. Invalid measurements cannot be classified.
#   6. Unknown assay profiles cannot be classified.
#   7. Measurement validity, classification, and evidence integrity are separate.
#   8. Never fabricate GPS, device metadata or test records.
#   9. Imported images must remain visibly labelled IMPORTED_IMAGE.
#   10. Synthetic benchmark metrics must never be presented as field accuracy.
#
# PRIMARY USER FLOW:
#   SETUP -> CAPTURE -> CHECK -> ANALYSIS -> RESULT -> EVIDENCE -> COMPLETE
#
# IMPLEMENT:
#
# A. SESSION:
#   persistent state machine
#   recover active sessions from SQLite
#
# B. CAPTURE:
#   live camera
#   reference card framing
#   reaction ROI guidance
#
# C. ADAPTIVE CAPTURE GUARD:
#   blur
#   exposure
#   glare
#   card detection
#   perspective
#   ROI visibility
#   provide actionable retake instructions
#
# D. VISION:
#   card localization
#   perspective warp
#   CIE Lab calibration
#   reaction ROI extraction
#
# E. PROFILE ENGINE:
#   load assay profile JSON
#   bind profile version to test record
#   disable uncalibrated real profiles
#
# F. CLASSIFIER:
#   nearest-centroid / explainable distance method for the synthetic MVP
#   positive
#   negative
#   inconclusive
#   invalid capture (handled before classifier)
#
# G. RESULT UI:
#   prominent "PRESUMPTIVE FIELD-TEST RESULT"
#   prominent "Laboratory confirmation is required."
#   show measured colour and decision explanation
#
# H. RELIABILITY PASSPORT:
#   capture
#   measurement
#   classification
#   evidence
#
# I. EVIDENCE:
#   SHA-256
#   canonical JSON
#   Ed25519
#   backward-linked hash chain
#   independent verification
#
# J. TIMELINE:
#   capture -> gate -> calibration -> classification -> sign -> seal -> export
#
# K. LAB HANDOFF:
#   JSON + HTML
#   no fake FSL result
#
# L. OFFLINE:
#   all core computation must work without internet
#   show sync state
#
# M. QA MODE:
#   synthetic scenarios
#   blur
#   glare
#   ambiguous
#   unknown profile
#   tamper
#   deleted chain link
#   imported image
#   offline
#
# REQUIRED TEST:
#   Make an integration assertion that the classifier function is never called
#   for a hard quality-gate failure.
#
# REQUIRED UX TEST:
#   A poor capture must tell the operator exactly what to fix.
#
# REQUIRED SECURITY TEST:
#   Editing result/operator/metric/image must fail verification.
#
# REQUIRED HONESTY TEST:
#   GPS unavailable must be displayed as unavailable.
#
# DO NOT introduce:
#   cloud-only dependencies,
#   LLM APIs for chemical identification,
#   generic drug-name inference from images,
#   fake legal claims,
#   blockchain dependencies,
#   real controlled substances.
#
# END MASTER BUILD PROMPT
#
# ---------------------------------------------------------------------------
# 57 — SOURCE-GROUNDED RESEARCH NOTES
# ---------------------------------------------------------------------------
#
# SIH26231:
#   The current published problem statement identifies subjectivity of visual
#   colour interpretation, lack of standardisation, absence of a verifiable
#   place/time record, reference-card calibration, automated outcome categories,
#   timestamp/GPS/operator ID, image hash, searchable log, signed digital record,
#   and the presumptive-not-confirmatory boundary.
#
# NCB / INDIAN FIELD CONTEXT:
#   NCB publications describe drug detection kits as "on the spot" testing tools
#   supplied to drug-law-enforcement agencies, and Indian forensic training
#   material describes comparing the colour reaction with the kit chart while
#   emphasizing that the kit is presumptive/preliminary and does not cover all
#   NDPS substances.
#
# COMMERCIAL PRIOR ART:
#   DetectaChem's MobileDetect product demonstrates automated smartphone-based
#   presumptive testing/reporting, including test images, date/time, GPS and
#   local result storage. DetectaChem also markets dedicated hardware such as
#   SEEKERe and newer spectroscopic/Raman/NIR products. REACTRA must therefore
#   avoid claiming these basic mobile/reporting ideas as novel.
#
# CURRENT INDIAN EVIDENCE LAW:
#   The Bharatiya Sakshya Adhiniyam, 2023 is the current central evidence statute
#   and has been in force since 1 July 2024. REACTRA should describe cryptographic
#   integrity/provenance cautiously and must not promise automatic admissibility.
#
# ---------------------------------------------------------------------------
# 58 — SOURCE LIST FOR THE PROJECT TEAM
# ---------------------------------------------------------------------------
#
# [S1] SIH 2026 Problem Statement SIH26231 — Digital Companion for Field Drug Testing
#      Source domain: sih2026.vuce.in
#
# [S2] Narcotics Control Bureau — official publications / Drug Detection Kits
#      Source domain: narcoticsindia.nic.in
#
# [S3] A Forensic Guide for Crime Investigators — spot-test guidance and cautions
#      Source domain: police.py.gov.in
#
# [S4] DetectaChem — MobileDetect field test kits and app
#      Source domain: detectachem.com
#
# [S5] DetectaChem — MobileDetect application update / local storage and Raman support
#      Source domain: detectachem.com
#
# [S6] India Code — Bharatiya Sakshya Adhiniyam, 2023
#      Source domain: indiacode.nic.in
#
# NOTE:
#   These sources ground the problem framing and product boundaries. They do not
#   by themselves establish that REACTRA's prototype thresholds, classifier,
#   calibration method, or cryptographic packaging are validated for operational
#   deployment. Those require separate engineering and authorised validation.
#
# ---------------------------------------------------------------------------
# 59 — FINAL "WHAT MAKES REACTRA DIFFERENT?" ANSWER
# ---------------------------------------------------------------------------
#
# If a judge asks:
#   "In one sentence, why should I remember your project?"
#
# Use:
#
#   "Because REACTRA does not simply recognize a colour — it first verifies that
#   the measurement is usable, explains a presumptive result only for the exact
#   configured test profile, and seals the complete event into a verifiable
#   evidence timeline."
#
# If the judge asks:
#   "What is your strongest innovation?"
#
# Use:
#
#   "Our core innovation is the integration of measurement validity, explainable
#   presumptive interpretation, and cryptographic evidence provenance into one
#   offline field workflow, with explicit handling of uncertainty and failure."
#
# If the judge asks:
#   "What is the one thing you refuse to do?"
#
# Use:
#
#   "We refuse to guess. If the image is invalid, the profile is unsupported, or
#   the reaction is ambiguous, REACTRA blocks or escalates instead of pretending
#   certainty."
#
# ---------------------------------------------------------------------------
# 60 — FINAL BUILD DEFINITION
# ---------------------------------------------------------------------------
#
# REACTRA V2 IS COMPLETE WHEN:
#
#   A trained operator can begin a field-test session,
#   capture a test beside a reference card,
#   receive immediate feedback when the image is unusable,
#   obtain a calibrated presumptive interpretation only when measurement conditions
#   are acceptable,
#   see exactly what was measured and which profile/version was used,
#   clearly see that the result is presumptive,
#   seal the event into an evidence record,
#   independently verify its cryptographic integrity,
#   search it later through a timeline,
#   and export a laboratory-referral package,
#
# all while remaining functional offline and without claiming to determine final
# chemical identity, legal status, guilt, or laboratory confirmation.
#
# THIS IS THE REACTRA V2 PRODUCT CONTRACT.
#
# ---------------------------------------------------------------------------
# END OF MASTER SPECIFICATION
# ---------------------------------------------------------------------------
