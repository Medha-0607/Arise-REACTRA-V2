# REACTRA — Product Requirements Document (PRD)
## Digital Companion for Field Drug Testing
### SIH 2026 — Problem Statement SIH26231
**Version:** 2.1 — 10/10 Revision  
**Date:** 22 September 2026  
**Source basis:** REACTRA Master Build Specification V2

---

# 1. Document Purpose

This Product Requirements Document (PRD) translates the REACTRA Master Build Specification V2 into an implementation-oriented product contract.

The PRD defines:

- the product problem and target users,
- the jobs REACTRA must help users complete,
- the end-to-end field workflow,
- functional and non-functional requirements,
- the MVP boundary,
- safety and forensic guardrails,
- evidence and audit requirements,
- prototype success criteria,
- demo requirements,
- product differentiation,
- roadmap priorities,
- and acceptance criteria for release.

This PRD is derived from the attached REACTRA V2 specification and preserves its central product boundaries and terminology.

---

# 2. Executive Summary

## 2.1 Product

REACTRA (Reaction-Aware Field Testing & Verifiable Evidence) is an offline-first field evidence companion for presumptive colorimetric drug testing.

REACTRA works alongside an existing field-test kit. It does not replace the chemical kit and does not replace confirmatory laboratory testing.

Its purpose is to improve the digital layer around the physical field test by:

1. guiding the operator to capture a usable image,
2. validating whether the measurement is suitable for interpretation,
3. calibrating the observed colour using an in-frame reference card,
4. generating an explainable presumptive interpretation for the configured assay profile,
5. making uncertainty and invalid measurements explicit,
6. preserving the complete event as a tamper-evident digital record,
7. maintaining a searchable evidence timeline,
8. and preparing a structured laboratory handoff.

## 2.2 Product Positioning

REACTRA is NOT an "AI drug detector."

The intended positioning is:

> **REACTRA is a Field Evidence Intelligence Layer that turns a subjective field colour test into a standardized, explainable and verifiable digital evidence event.**

The product should communicate three actions:

### MEASURE
Standardize the visual observation and reject unusable captures.

### EXPLAIN
Show why a presumptive result was generated, withheld, or escalated.

### PRESERVE
Seal the event into a verifiable evidence record and timeline.

---

# 3. Product Context

## 3.1 Problem Statement

The product addresses two connected problems.

### Problem A — Measurement Standardisation

Traditional colorimetric field testing can require a human operator to visually interpret a colour change under variable field conditions.

Potential sources of variability include:

- operator-to-operator colour interpretation,
- nighttime or uneven lighting,
- blur and poor exposure,
- specular glare,
- incorrect framing,
- reference-card visibility problems,
- camera variability,
- reaction timing,
- reagent condition,
- and ambiguous colour transitions.

### Problem B — Digital Traceability

The field test is also a recordkeeping event.

REACTRA must convert that momentary observation into a structured, searchable and tamper-evident digital event containing relevant provenance and analytical metadata.

## 3.2 Product Context in the Indian Field Workflow

The exact legal procedure varies by the facts of the encounter, the location, the officer's statutory authority, the type of search, and applicable departmental SOPs. REACTRA therefore models the operational evidence workflow without attempting to automate legal judgment.

The product context is broadly:

**Encounter / intelligence / checkpoint event**  
→ **Lawful interception/search/recovery under applicable authority**  
→ **Suspected material identified for further examination**  
→ **Presumptive field-test procedure using the applicable approved/configured kit**  
→ **Reaction timer started at the protocol-defined reaction start point**  
→ **Reaction observed and documented inside the configured kinetic window**  
→ **Presumptive field result recorded**  
→ **Seizure / inventory / sampling / sealing / documentation as required by law and SOP**  
→ **Forensic laboratory confirmation**  
→ **Investigation / case record / judicial process**

REACTRA begins at the approved field-test stage and continues into evidence documentation and laboratory handoff.

### 3.2.1 Indian statutory context represented in REACTRA

The NDPS Act contains distinct powers and safeguards for different circumstances, including public-place seizure/arrest, conveyance searches, and personal searches. Section 50 concerns conditions for personal search and provides a right, when applicable and invoked, to be taken without unnecessary delay to a nearest Gazetted Officer or Magistrate. Section 52A addresses post-seizure inventory, photographs and representative samples in the presence of a Magistrate under the statutory procedure. Section 57 concerns reporting of arrest/seizure to the immediate superior.

For applicable place-search procedures, the Bharatiya Nagarik Suraksha Sanhita (BNSS) contains general search provisions addressing the calling of independent and respectable inhabitants to witness certain searches and the preparation/signing of the seizure list.

### 3.2.2 REACTRA statutory boundary

REACTRA MAY:

- record procedural references supplied by the officer;
- preserve witness and memo metadata;
- track whether a relevant procedural step was recorded inside or outside REACTRA;
- carry sample/seal/inventory references into a laboratory handoff;
- provide configurable procedural reminders.

REACTRA MUST NOT:

- decide whether a statutory provision applies;
- decide whether a search was lawful;
- replace the officer's required statutory actions;
- certify legal compliance merely because fields were completed;
- replace a Magistrate's role;
- replace laboratory confirmation;
- or present a presumptive colour reaction as a final legal or chemical finding.

### 3.2.3 Product principle

> **REACTRA records and verifies what happened in the digital workflow; it does not decide what the law means.**

# 4. Product Goals

## 4.1 Primary Goals

### G1 — Improve measurement usability
Prevent poor images from reaching the classification stage.

### G2 — Reduce subjective colour interpretation
Use a reference card and calibrated colour analysis to support standardized interpretation.

### G3 — Make uncertainty visible
Support explicit:
- PRESUMPTIVE POSITIVE
- PRESUMPTIVE NEGATIVE
- INCONCLUSIVE
- INVALID CAPTURE

### G4 — Preserve provenance
Bind each test to its:
- operator,
- test/case identifier,
- timestamp,
- location provenance,
- capture mode,
- assay profile/version,
- reference-card version,
- algorithm/model version,
- and relevant measurement metadata.

### G5 — Make the record tamper-evident
Use:
- SHA-256,
- canonical record serialization,
- Ed25519 signatures,
- and a backward-linking local audit chain.

### G6 — Support evidence continuity
Provide a searchable timeline and laboratory referral package.

### G7 — Work offline
Core capture, analysis, evidence sealing, verification, search and export must not require internet access.

### G8 — Maintain scientific and legal honesty
The product must not claim:
- laboratory confirmation,
- legal guilt,
- unlawful possession,
- automatic legal admissibility,
- or identification of an unsupported substance/profile.

---

# 5. Non-Goals

REACTRA will NOT:

1. perform or automate statutory search/arrest decisions;
2. determine whether possession is legally permitted;
3. determine guilt or innocence;
4. replace departmental safeguards or SOPs;
5. replace seizure, sampling or sealing acts that require official procedure;
6. perform laboratory chemical identification;
7. generate fake laboratory/FSL reports;
8. identify any arbitrary drug from a generic photograph;
9. fabricate GPS or device metadata;
10. turn synthetic benchmark results into claims of field accuracy;
11. require blockchain to function;
12. require a cloud service for core operation.

---

# 6. Target Users

## 6.1 Primary User — Trained Field Operator

Examples:

- drug-law-enforcement field officer,
- designated screener,
- trained enforcement personnel using an approved field-test kit.

### User characteristics
- works under time pressure,
- may operate outdoors or at night,
- may have intermittent/no connectivity,
- should not be exposed to developer-level diagnostics during routine use,
- needs clear action-oriented guidance.

### Primary job
> Conduct and document a configured presumptive field test with minimum ambiguity and maximum traceability.

---

## 6.2 Secondary User — Supervisor / Reviewer

Needs to:

- review field-test records,
- inspect result rationale,
- inspect measurement quality,
- review evidence integrity,
- search by operator/case/date/result/profile,
- and identify records requiring review or referral.

---

## 6.3 Secondary User — Laboratory / Forensic Recipient

Needs to receive a structured handoff containing:

- identifiers,
- field-test result,
- provenance,
- measurement metadata,
- original image digest,
- evidence record digest,
- signature status,
- chain link,
- and operator-entered sample/evidence identifiers.

REACTRA must explicitly state that laboratory confirmation remains required.

---

## 6.4 Secondary User — Evidence / Audit Personnel

Needs to independently verify:

- record digest,
- signature,
- image integrity,
- and chain continuity.

---

# 7. Jobs-To-Be-Done

## JTBD-1 — Capture

> When conducting a field test, help me capture the reaction and reference card correctly without requiring me to understand computer vision.

## JTBD-2 — Validate

> When lighting or image quality is poor, tell me what is wrong and what I should fix before proceeding.

## JTBD-3 — Interpret

> When the capture is valid, provide a transparent presumptive interpretation for the exact configured assay profile.

## JTBD-4 — Escalate Uncertainty

> When the evidence is ambiguous, do not force a positive or negative result. Give me a clear review/referral path.

## JTBD-5 — Preserve

> When a field-test event is completed, automatically preserve its image, metadata and analytical context as a verifiable record.

## JTBD-6 — Reconstruct

> When the event must be reviewed later, let me reconstruct what happened through a chronological evidence timeline.

## JTBD-7 — Handoff

> When laboratory confirmation is required, produce a structured packet containing the field-test information without fabricating laboratory findings.

---

# 8. Product Principles

## P1 — REACTRA Refuses to Guess

If:
- the image is invalid,
- the profile is unsupported,
- or the reaction is ambiguous,

REACTRA blocks, escalates or records uncertainty instead of inventing certainty.

## P2 — Validity Before Classification

The product must never classify an image that failed a hard measurement-quality gate.

## P3 — Profile Before Interpretation

A result must always be tied to an explicit assay profile/version.

No generic one-size-fits-all colour classifier.

## P4 — Evidence Integrity Is Separate from Classification

A digitally trustworthy record does not mean the chemical interpretation is confirmed.

## P5 — Offline by Default

The core field workflow must operate without network access.

## P6 — Honest Metadata

GPS, imported-image status and other provenance information must reflect reality.

## P7 — Operator Assistance, Not Autonomous Enforcement

REACTRA supports trained personnel and applicable SOPs. It does not make enforcement decisions.

## P8 — Scientific Transparency

The prototype must show what was measured and how the result was obtained without presenting model output as chemical truth.

---

# 9. End-to-End User Journey

## Stage 0 — Authentication

Operator opens REACTRA.

System:
- authenticates/operator-identifies user,
- creates or restores an active session,
- shows offline/sync state.

---

## Stage 1 — START FIELD TEST

Operator enters/selects:

- Test Session ID (automatic)
- Operator ID (required)
- Case/Event ID
- Assay/KIt Profile
- Kit Lot/Batch if available
- Kit Expiry/Validity if available
- Capture Mode
- Location Status

### Guardrails

- unsupported profile → analysis blocked;
- uncalibrated real profile → operational classification blocked;
- fake/default coordinates → prohibited;
- imported image remains visibly labelled IMPORTED_IMAGE.

---

## Stage 2 — ADAPTIVE CAPTURE GUARD

REACTRA becomes a measurement assistant.

### On-screen guidance

- reference-card outline;
- reaction-zone guide;
- low-light guidance;
- glare guidance;
- framing assistance.

### Capture checks

A. Reference card visible?  
B. Required fiducials visible?  
C. Image sharp enough?  
D. Exposure usable?  
E. Glare acceptable?  
F. Reaction ROI visible?  
G. Perspective correction possible?  
H. Correct profile identifiable?

### Failure behaviour

Do not classify.

Instead display a precise instruction.

Examples:

**CAPTURE INVALID**  
Reference card not detected.  
**Action:** Include the complete reference card and retake.

**CAPTURE INVALID**  
Excessive glare.  
**Action:** Change angle/lighting and retake.

**CAPTURE INVALID**  
Motion blur.  
**Action:** Hold device steady and retake.

This is a core product differentiator.

---

# 10. Measurement Quality Model

## 10.1 Required Quality Dimensions

### Blur
Measure image sharpness using a configured blur metric.

### Exposure
Measure usable brightness/dynamic range.

### Glare
Measure saturated/high-specular pixel fraction.

### Card Detection
Measure reference-card geometry/fiducial confidence.

### Calibration
Measure reference-patch calibration residual.

### ROI
Confirm the reaction region is visible and sufficiently populated.

## 10.2 Important Product Rule

Prototype thresholds are engineering parameters.

They must NOT be described as validated forensic or legal standards unless they have been experimentally established for the exact:

- camera,
- reference card,
- kit,
- reagent,
- environment,
- and operating procedure.

---

# 11. Measurement Pipeline

## 11.1 Reaction Kinetic Windowing

Colorimetric reactions are time-dependent. The same reagent can produce materially different colour observations at different elapsed times. REACTRA therefore treats reaction time as part of the measurement context rather than optional metadata.

### Protocol-defined parameters

Every timing-dependent assay profile must define:

- `t_min_seconds`: minimum elapsed time after the protocol-defined reaction start before capture can be interpreted.
- `t_max_seconds`: maximum elapsed time after reaction start after which the capture is invalid for interpretation.

These are profile-specific protocol parameters, not universal chemistry constants. The hackathon prototype must use synthetic/demo values unless validated authorised assay data are available.

### Reaction Ingestion Timer

The Capture Guard must display:

- `REACTION TIMER`;
- elapsed time;
- `WAITING FOR VALID WINDOW`, `WITHIN VALID WINDOW`, or `WINDOW EXPIRED`;
- configured `t_min` and `t_max`;
- capture action state.

The timer starts when the operator performs an explicit `START REACTION` action at the protocol-defined reaction start point. The start event is persisted as an audit event.

### Hard kinetic gate

If:

`capture_elapsed_seconds < t_min_seconds`

then:

`INVALID_CAPTURE: OUTSIDE_VALID_KINETIC_WINDOW`

with corrective action:

> **WAIT — REACTION WINDOW NOT REACHED.**  
> Capture becomes valid at `<t_min>` seconds.

If:

`capture_elapsed_seconds > t_max_seconds`

then:

`INVALID_CAPTURE: OUTSIDE_VALID_KINETIC_WINDOW`

with corrective action:

> **REACTION WINDOW EXPIRED.**  
> Start a new test according to the applicable procedure.

The classifier must not execute in either case.

### Timing provenance

For `LIVE_CAMERA`:

- record reaction-start timestamp;
- record capture timestamp;
- calculate elapsed time from a monotonic clock;
- retain wall-clock timestamps separately for evidence provenance.

For `IMPORTED_IMAGE`:

- elapsed time must come from trusted source metadata or an explicitly labelled operator/demo entry;
- an operational timing-dependent classification is blocked if the required kinetic timing evidence is unavailable.

### Timing status values

- `BEFORE_WINDOW`
- `IN_WINDOW`
- `AFTER_WINDOW`
- `UNKNOWN`

`UNKNOWN` is non-classifiable for profiles that require kinetic windowing.

## 11.2 Measurement Pipeline

The authoritative pipeline is:

**SETUP**  
→ **REACTION TIMER START**  
→ **CAPTURE**  
→ **KINETIC WINDOW GATE**  
→ **QUALITY GATE**  
→ **if FAIL: STOP**  
→ **CARD LOCALIZATION**  
→ **PERSPECTIVE WARP**  
→ **COLOUR CALIBRATION**  
→ **LIQUID ROI SEGMENTATION & ROBUST SAMPLING**  
→ **CLASSIFICATION**

The service layer must enforce this pipeline, not only the UI.

## 11.3 Required Quality Metrics

### Blur
Measure image sharpness using a configured blur metric.

### Exposure
Measure usable brightness/dynamic range.

### Glare
Measure saturated/high-specular pixel fraction.

### Card Detection
Measure reference-card geometry/fiducial confidence.

### Calibration
Measure reference-patch calibration residual.

### ROI
Confirm the reaction region is visible and sufficiently populated after reflection/background filtering.

## 11.4 Pipeline Enforcement Rule

If any hard gate fails:

- classifier invocation count must remain zero;
- `classification_result` must remain null;
- the session enters `VALIDATION_FAILED`;
- the UI provides a corrective action.

## 11.5 Threshold Governance

Prototype thresholds are engineering parameters.

They must NOT be described as validated forensic or legal standards unless experimentally established for the exact camera, reference card, kit, reagent, environment and operating procedure.

# 12. Four-State Outcome Model

## 12.1 PRESUMPTIVE POSITIVE

A valid calibrated capture falls within the configured positive region.

UI:

**PRESUMPTIVE POSITIVE FOR THE CONFIGURED TEST PROFILE**

## 12.2 PRESUMPTIVE NEGATIVE

A valid calibrated capture falls within the configured negative region for the configured assay/protocol.

UI:

**PRESUMPTIVE NEGATIVE FOR THE CONFIGURED TEST PROFILE**

## 12.3 INCONCLUSIVE

Use when:
- the reaction lies near configured class boundaries,
- colour is ambiguous,
- or the configured assay does not support a sufficiently clear interpretation.

UI:

**INCONCLUSIVE — REVIEW / LABORATORY CONFIRMATION REQUIRED**

## 12.4 INVALID CAPTURE

Use when the image itself is not suitable for interpretation.

UI:

**INVALID CAPTURE — NO CLASSIFICATION GENERATED**

### Key distinction

**INCONCLUSIVE** = measurement may be valid, interpretation is unclear.

**INVALID CAPTURE** = measurement itself is unacceptable.

---

# 13. Reference Card and Colour Calibration

## 13.1 Purpose

The reference card is a calibration reference, not a decorative UI object.

REACTRA must use it to support normalization of observed colour under the current capture conditions.

## 13.2 Required Functions

- detect QR/profile marker where available;
- detect four-corner fiducials;
- estimate card quadrilateral;
- reject severe occlusion;
- perspective warp;
- sample reference patches;
- record detection metrics.

## 13.3 Calibration Approach

Prototype implementation:

- CIE L*a*b* representation;
- least-squares affine transformation;
- Delta E76 residual measurement.

The PRD does not claim this approach solves every physical illumination, camera, lens or chemical variation.

---

# 14. Reaction Region of Interest

## 14. Reaction Region of Interest

REACTRA must isolate the **reactive liquid/solution region** rather than treating every pixel in the visual box as chemically meaningful.

The system must distinguish:

- reference patches,
- reaction ROI,
- pouch/container boundaries,
- background,
- bubbles/solid particles where visually detectable,
- reflections/glare,
- and the reactive solution.

The evidence record must preserve the ROI geometry and sampling method used.

## 14.1 Required Liquid-ROI Sampling Algorithm

### Step 1 — Initial ROI definition

Obtain the reaction ROI from the configured assay profile or the validated ROI detector.

Record:

- ROI bounding box/polygon;
- pixel count;
- detector confidence;
- profile/version.

### Step 2 — Convert ROI to calibrated CIE L*a*b*

Transform the raw ROI into the same calibrated CIE L*a*b* space used by the classification pipeline.

### Step 3 — Reflection/specular rejection

Mask candidate high-specular pixels before colour estimation.

Prototype rejection conditions include:

- `L* > 95`, OR
- configured saturation/specular threshold exceeded.

Record:

- total ROI pixels;
- rejected specular pixels;
- rejection fraction.

### Step 4 — Spatial colour filtering

Run spatial colour clustering to separate the reactive liquid from pouch/background structure.

Prototype default:

- K-means with `k = 3`;
- deterministic random seed;
- configured iteration and initialization limits;
- operate only on non-specular ROI pixels.

The implementation may reduce to `k = 2` when the ROI is too small for the default configuration, but the selected `k` must be stored in the measurement record.

### Step 5 — Dominant reaction-cluster selection

Select the cluster representing the dominant reactive-solution region using deterministic spatial and area rules defined by the assay profile.

Selection should prefer a cluster that:

- occupies a substantial contiguous portion of the central reaction ROI;
- lies inside the expected liquid region;
- is not dominated by pouch/background boundary pixels.

### Step 6 — Robust colour estimate

Do **not** use a naive arithmetic mean of all ROI pixels.

Compute the **median CIE L*a*b* vector** of the selected dominant reaction cluster:

`reaction_lab = median(cluster_pixels_lab, axis=0)`

This reduces sensitivity to bubbles, suspended particles, small glare remnants and edge outliers.

### Step 7 — Save sampling diagnostics

The evidence record must preserve:

- sampling algorithm/version;
- K-means `k`;
- valid pixel count;
- rejected specular pixel count/fraction;
- selected cluster identifier;
- selected cluster area fraction;
- median L*a*b* vector;
- ROI geometry.

## 14.2 Explainability Requirement

The UI should display:

- original image;
- corrected image;
- card boundary;
- reference patches;
- reaction ROI;
- rejected/high-specular overlay where useful;
- selected reaction cluster overlay;
- resulting colour swatch.

The operator/reviewer should be able to understand:

> **This is the region REACTRA measured, and these are the pixels it excluded before calculating the representative colour.**

## 14.3 Hard ROI Failure

If the remaining valid reaction pixels are below the profile minimum:

`INVALID_CAPTURE: INSUFFICIENT_VALID_ROI_PIXELS`

The classifier must not run.

# 15. Assay / Kit Profile Engine

## 15. Assay / Kit Profile Engine

REACTRA is profile-driven.

A profile is the contract that tells the measurement and classification engines how to interpret a particular configured test workflow.

## 15.1 Profile Data

Each profile shall include:

- `profile_id`;
- `profile_name`;
- `profile_version`;
- `manufacturer_or_source` where applicable;
- `reference_card_version`;
- `supported_outcomes`;
- `calibration_targets`;
- `quality_thresholds`;
- `t_min_seconds`;
- `t_max_seconds`;
- `kinetic_window_required`;
- `reaction_start_definition`;
- `reaction_roi_definition`;
- `roi_sampling_method`;
- `roi_kmeans_k`;
- `roi_min_valid_pixels`;
- `specular_Lstar_threshold`;
- `specular_saturation_threshold`;
- positive feature/centroid configuration;
- negative feature/centroid configuration;
- `inconclusive_margin`;
- classifier configuration;
- safety notes;
- profile status.

## 15.2 Example Profile Schema

```json
{
  "profile_id": "DEMO-ASSAY-001",
  "profile_name": "Synthetic Demonstration Assay",
  "profile_version": "2.0",
  "reference_card_version": "2.0",
  "kinetic_window_required": true,
  "t_min_seconds": 10,
  "t_max_seconds": 60,
  "reaction_start_definition": "OPERATOR_START_REACTION",
  "roi_sampling_method": "kmeans_dominant_cluster_median_lab_v1",
  "roi_kmeans_k": 3,
  "roi_min_valid_pixels": 500,
  "specular_Lstar_threshold": 95.0,
  "specular_saturation_threshold": 0.98,
  "supported_outcomes": [
    "PRESUMPTIVE_POSITIVE",
    "PRESUMPTIVE_NEGATIVE",
    "INCONCLUSIVE"
  ],
  "inconclusive_margin_delta_e": 12.0,
  "quality_thresholds": {
    "blur_min": 80.0,
    "glare_fraction_max": 0.05,
    "calibration_delta_e_max": 8.0
  },
  "status": "DEMO_ONLY"
}
```

All numeric values above are prototype engineering parameters, not validated operational chemistry parameters.

## 15.3 Profile States

- CALIBRATED
- DEMO_ONLY
- STAGED
- DISABLED

## 15.4 Profile Activation Rules

If a real kit lacks validated physical calibration or timing data:

- mark STAGED or DEMO_ONLY;
- display warning;
- block operational-style classification;
- do not invent chemical centroids, kinetic limits or colour thresholds.

## 15.5 Version Immutability

Once a profile version has been used for a sealed evidence record, that record must retain the exact profile configuration snapshot used.

Later changes create a new profile version rather than modifying historical configuration in place.

## 15.6 Kinetic Configuration Governance

`t_min_seconds` and `t_max_seconds` are part of the assay protocol definition.

The application must not silently substitute timing values from another kit/profile.

A timing-dependent profile missing valid kinetic configuration results in:

`NO_OPERATIONAL_PROFILE: MISSING_KINETIC_CONFIGURATION`

# 16. Explainable Presumptive Classifier

The synthetic MVP may retain a nearest-centroid approach in calibrated CIE L*a*b* space.

The classifier should expose:

- measured colour;
- nearest class;
- runner-up class;
- nearest-class distance;
- second-class distance;
- separation margin;
- decision rule;
- profile version;
- algorithm/model version.

## 16.1 Decision Rule

If the classification margin is insufficient:

→ **INCONCLUSIVE**

Never force a positive/negative decision simply because one class is marginally closer.

## 16.2 Prohibited Language

Do not display:

- "98.2% chance this is cocaine"
- "99.99% AI certainty"
- "Definitely cocaine"
- "Drug confirmed"

Preferred wording:

- "Presumptive Positive — configured profile"
- "Decision margin: <value>"
- "Classification generated from calibrated colour distance"

---

# 17. Unknown / Unmatched Profile

If the captured test does not correspond to a supported assay profile:

**NO MATCHING ASSAY PROFILE**

Then:

- no automated chemical classification;
- capture preserved;
- event recorded for review;
- laboratory/SOP path made available.

REACTRA must never infer drug identity from generic image appearance.

---

# 18. Expiry / Degraded Reagent Handling

Available metadata should include:

- kit lot/batch;
- expiry/validity state.

If expired, unknown or otherwise questionable:

- flag status;
- prevent false confidence;
- use review/inconclusive pathways where appropriate;
- support laboratory referral.

Advanced reaction-kinetic analysis remains a future research feature.

---

# 19. Result Screen Requirements

## 19.1 Information Hierarchy

### Header

**PRESUMPTIVE FIELD-TEST RESULT**

**Laboratory confirmation is required.**

### Primary outcome

One of:

- PRESUMPTIVE POSITIVE
- PRESUMPTIVE NEGATIVE
- INCONCLUSIVE — REVIEW
- INVALID CAPTURE — RETAKE

### Supporting explanation

- Profile ID/version
- Measurement status
- Measured colour
- Nearest reference
- Decision margin
- Quality status

### Visual explanation

- original capture
- corrected capture
- card boundary
- reaction ROI
- reference patches

---

# 20. Case / Legal Context UX

## 20. Case / Legal Context UX

REACTRA must separate:

## Substance Test Result

The presumptive interpretation produced by the configured field test.

from:

## Case / Legal / Procedural Context

Operator-entered and workflow-recorded information describing the surrounding event.

### 20.1 Required procedural fields

The case/evidence context schema shall support:

- `case_id`
- `event_id`
- `field_officer_name`
- `field_officer_designation`
- `police_station_jurisdiction`
- `panchnama_memo_ref_no`
- `panch_witness_1_name`
- `panch_witness_2_name`
- `search_context_type`
- `procedural_safeguard_status`
- `authorization_reference`
- `officer_notes`

Where relevant/applicable under the governing procedure or departmental SOP, REACTRA may also capture:

- `section_50_status`
- `section_50_choice_recorded`
- `gazetted_officer_or_magistrate_reference`
- `inventory_ref_no`
- `section_52a_reference`
- `seal_identifier`
- `sample_identifier`
- `sample_drawal_status`
- `magistrate_certification_status`
- `section_57_report_ref_no`
- `section_57_report_status`

These are recordkeeping fields, not an automated legal-compliance engine.

### 20.2 Panch-witness handling

REACTRA should make panch-witness fields available for applicable search/seizure workflows without asserting that two independent witnesses are universally mandatory for every NDPS recovery.

Supported states:

- `WITNESS_DATA_RECORDED`
- `NOT_APPLICABLE_OR_NOT_REQUIRED_BY_CURRENT_SOP`
- `RECORDED_OUTSIDE_REACTRA`
- `PENDING_PROCEDURAL_RECORD`

The app must not prevent the field-test measurement solely because witness metadata is absent unless the deploying authority explicitly configures such a gate.

### 20.3 Legal-status separation

The legal conclusion is outside REACTRA's automated authority.

Do not equate:

**Positive = Guilty**

**Positive = Illegal possession**

**Negative = Nothing illegal**

Preferred copy:

> **PRESUMPTIVE FIELD-TEST RESULT**  
> This result does not determine legal status or final chemical identity.

### 20.4 Statutory procedure awareness

REACTRA may surface a configurable checklist/reminder based on the encounter/search context, but checklist completion is not legal certification.

Every procedural field must retain whether the information was:

- captured by REACTRA;
- entered manually;
- referenced from another official record;
- or unavailable.

# 21. Evidence Reliability Passport

Every completed field test receives a four-part Reliability Passport.

## Section A — Capture

Include:

- test_id;
- timestamp;
- operator_id;
- capture_mode;
- location source/status;
- device/camera metadata where reliably available;
- original image digest.

## Section B — Measurement

Include:

- card detection;
- card profile/version;
- calibration method;
- calibration residual;
- blur metric;
- exposure metric;
- glare metric;
- ROI status;
- quality gate status.

## Section C — Classification

Include:

- configured profile;
- profile version;
- result;
- class distances;
- decision margin;
- algorithm/model version;
- explicit presumptive label.

## Section D — Evidence Integrity

Include:

- image SHA-256;
- canonical record digest;
- Ed25519 signature status;
- public key fingerprint;
- previous record hash;
- chain verification state.

---

# 22. Reliability Status Model

## READY

Measurement valid + presumptive result generated + evidence sealed.

## REVIEW

Ambiguous or soft condition and/or inconclusive result.

## RECAPTURE

Hard measurement failure. Classification blocked.

## REFERRAL REQUIRED

Test/case requires progression toward laboratory examination according to SOP.

Do not use:

- "Court Admissible"
- "Legally Proven"
- "Forensically Confirmed"

as product badges.

---

# 23. Evidence Integrity Model

REACTRA must visually separate:

### Classification

> What did the calibrated test result resemble?

from:

### Evidence Integrity

> Can the digital record be verified as internally consistent and cryptographically intact?

Example:

**Classification:**  
PRESUMPTIVE POSITIVE

**Evidence Integrity:**  
VERIFIED

This does NOT make the chemical result laboratory-confirmed.

Another valid state:

**Classification:**  
INCONCLUSIVE

**Evidence Integrity:**  
VERIFIED

---

# 24. Cryptographic Evidence Requirements

## 24. Cryptographic Evidence Requirements

Preserve the existing architecture:

- SHA-256 image hashing;
- canonical JSON;
- Ed25519 signatures;
- backward-linking hash chain;
- local SQLite persistence;
- portable evidence envelope.

## 24.1 Canonicalization

Use:

`json-sort-keys-compact-utf8-v1`

## 24.2 Signed Content

The signed record must bind relevant:

- identifiers;
- timestamps;
- operator information;
- device enrollment identity;
- profile/version data;
- kinetic-window data;
- ROI sampling data;
- measurement status;
- classification data;
- procedural reference metadata;
- provenance;
- image digest;
- previous record hash.

## 24.3 Device Enrollment & Key Attestation

Ed25519 provides cryptographic signing; it does not by itself establish that the key belongs to an authorized field device.

REACTRA therefore requires a separate **device enrollment and trust-registry layer**.

### Enrollment lifecycle

1. An authorized administrator creates a device enrollment record.
2. The device generates its Ed25519 keypair locally during first activation.
3. The private key is generated on-device and never enters an evidence envelope.
4. The device public key fingerprint is submitted through the approved enrollment process.
5. The issuing authority binds the key to:
   - `device_enrollment_id`;
   - a device/platform identity;
   - issuing authority;
   - activation/validity dates;
   - device status.
6. The authority signs the trusted device registry.
7. The device stores the authority-signed registry needed for offline verification.

### Trusted registry schema

```json
{
  "registry_version": "1.0",
  "issuer_id": "AUTHORITY-DEMO-001",
  "issued_at_utc": "2026-09-22T12:00:00Z",
  "devices": [
    {
      "device_enrollment_id": "DEV-001",
      "public_key_fingerprint": "SHA256:abcd...",
      "device_attestation_id": "ATTEST-001",
      "status": "ACTIVE",
      "valid_from_utc": "2026-09-22T12:00:00Z",
      "valid_until_utc": null
    }
  ],
  "registry_signature": "<authority-signature>"
}
```

`trusted_public_keys.json` must be treated as a **signed trust registry**, not as an ordinary editable configuration file.

### Verifier requirements

`verifier.py` shall:

1. verify the authority signature on the trust registry;
2. locate the evidence record's signing public-key fingerprint;
3. verify that the key is registered;
4. verify that the key status is active and valid for the relevant time;
5. verify the Ed25519 signature over the evidence digest.

Verification outputs must distinguish:

- `SIGNATURE_VALID`
- `SIGNING_DEVICE_AUTHORIZED`
- `SIGNING_DEVICE_REVOKED`
- `SIGNING_KEY_UNKNOWN`
- `TRUST_REGISTRY_INVALID`

### Reinstallation / key replacement

A fresh installation must not self-authorize a new signing key.

A new key becomes trusted only through authorized enrollment/activation.

A revoked/superseded key must fail device authorization even if its mathematical signature is valid.

### Prototype note

If true platform hardware attestation is unavailable in the Streamlit MVP, the trust-registry mechanism may be demonstrated with an explicit simulated `device_attestation_id`. The UI and documentation must label that status as prototype-only.

## 24.4 Canonical Evidence Fields

At minimum the signed evidence record shall include:

- `evidence_format_version`
- `test_id`
- `case_id`
- `event_id`
- `timestamp_utc`
- `reaction_started_at_utc`
- `capture_timestamp_utc`
- `capture_elapsed_seconds`
- `timer_source`
- `operator_id`
- `field_officer_designation`
- `device_enrollment_id`
- `signing_key_fingerprint`
- `capture_mode`
- `gps_status`
- `latitude`
- `longitude`
- `location_accuracy`
- `assay_profile_id`
- `assay_profile_version`
- `reference_card_version`
- `algorithm_version`
- `model_version`
- `quality_gate_status`
- `measurement_quality`
- `kinetic_window_status`
- `result`
- `classification_metrics`
- `roi_sampling_metadata`
- `procedural_reference_metadata`
- `image_sha256`
- `previous_record_hash`

The envelope adds:

- `record_digest`
- `signature`
- `public_key_fingerprint`
- `canonical_algorithm`
- `trust_registry_version`
- `signing_device_authorization_status`

## 24.5 Trust Boundary

Cryptography makes the stored record tamper-evident within its trust model.

It does not prove that a compromised device, camera, operator input or operating system captured truthful information before signing.

# 25. Image Provenance

Every image must be labelled:

- LIVE_CAMERA
- IMPORTED_IMAGE

Imported images are permitted for QA/demo workflows.

They must remain visibly marked as imported and must never be presented as a contemporaneous live field capture.

Record:

- capture_mode;
- ingestion timestamp;
- image SHA-256;
- dimensions;
- source label;
- available device metadata.

---

# 26. Location Requirements

Supported states:

## GPS_DEVICE
Genuine device-provided coordinates.

## UNAVAILABLE
Trusted coordinates are unavailable.

## MANUAL_DEMO
Explicit hackathon/demo-only coordinates.

### Prohibited

- silent IP geolocation;
- fabricated coordinates;
- manual coordinates represented as device GPS;
- unsupported location precision.

---

# 27. Offline-First Requirements

Core functionality must work without internet:

- capture;
- quality gate;
- calibration;
- configured-profile classification;
- evidence hashing;
- digital signature;
- local storage;
- history search;
- integrity verification;
- export.

Network may be used later for:

- synchronization;
- supervisory upload;
- central case integration;
- laboratory gateway integration.

## Sync states

- LOCAL_ONLY
- PENDING_SYNC
- SYNCED
- SYNC_FAILED

The UI must not imply central receipt simply because the record exists locally.

---

# 28. Evidence Timeline

Every test should expose an ordered chain of events.

Example:

1. Session created
2. Operator authenticated
3. Capture initiated
4. Image accepted
5. Quality gate passed
6. Calibration completed
7. Presumptive interpretation generated
8. Officer reviewed result
9. Evidence record signed
10. Local chain committed
11. Exported or queued for synchronization

The timeline is a reconstruction aid and does not replace official logs.

---

# 29. Laboratory Handoff

## 29. Laboratory Handoff

### 29.1 Purpose

Move the field-test record forward without pretending it is a laboratory finding.

The handoff should contain both the scientific context of the presumptive field test and the procedural identifiers needed to locate the surrounding case/evidence record.

### 29.2 Outputs

- `REACTRA_REFERRAL_<test_id>.json`
- `REACTRA_REFERRAL_<test_id>.html`

### 29.3 Packet Schema

```json
{
  "handoff_version": "1.0",
  "test_id": "RX-...",
  "case_id": "CASE-...",
  "event_id": "EVENT-...",
  "operator": {
    "operator_id": "OP-...",
    "field_officer_name": "...",
    "field_officer_designation": "...",
    "police_station_jurisdiction": "..."
  },
  "field_test": {
    "assay_profile_id": "DEMO-ASSAY-001",
    "assay_profile_version": "2.0",
    "reference_card_version": "2.0",
    "reaction_started_at_utc": "...",
    "capture_timestamp_utc": "...",
    "capture_elapsed_seconds": 24.3,
    "kinetic_window_status": "IN_WINDOW",
    "presumptive_result": "PRESUMPTIVE_POSITIVE",
    "quality_status": "READY"
  },
  "procedure": {
    "panchnama_memo_ref_no": "...",
    "panch_witness_1_name": "...",
    "panch_witness_2_name": "...",
    "inventory_ref_no": "...",
    "section_52a_reference": "...",
    "sample_identifier": "...",
    "seal_identifier": "...",
    "sample_drawal_status": "...",
    "magistrate_certification_status": "..."
  },
  "provenance": {
    "capture_mode": "LIVE_CAMERA",
    "gps_status": "GPS_DEVICE",
    "latitude": null,
    "longitude": null
  },
  "integrity": {
    "image_sha256": "...",
    "record_digest": "...",
    "signature_status": "VALID",
    "signing_device_authorization_status": "AUTHORIZED",
    "previous_record_hash": "..."
  },
  "notice": "Field result is presumptive. Laboratory confirmation required."
}
```

Fields whose statutory applicability varies must be nullable and/or carry an explicit applicability/status value.

### 29.4 Procedural separation

REACTRA records references to:

- panchnama/seizure memo;
- inventory;
- sample;
- seal;
- Magistrate-related certification;
- relevant reporting reference;

but it does not perform or certify those official acts.

### 29.5 Prohibited Outputs

Never generate:

- fake GC-MS report;
- fake FSL result;
- fake chemical identification certificate;
- fake Magistrate certification;
- fake seizure/panchnama document.

# 30. Searchable History

Minimum filters:

- Test ID
- Case ID
- Operator
- Date/time range
- Result
- Measurement status
- Integrity status
- Assay profile
- Sync state

Each result card should show:

- test ID;
- date/time;
- operator;
- result;
- status;
- profile;
- evidence-integrity state.

Opening a record should expose:

- Reliability Passport;
- Evidence Timeline;
- original/corrected image;
- verification status;
- referral/export actions.

---

# 31. Primary Information Architecture

## Main Navigation

1. NEW TEST
2. ACTIVE TEST
3. HISTORY
4. VERIFY EVIDENCE

## Secondary / QA

5. VALIDATION / QA MODE
6. BENCHMARKS
7. TAMPER DEMOS
8. DEBUG LOGS

Developer tooling must not contaminate the primary operator experience.

---

# 32. Required Screens

## Screen 01 — Splash / Authentication

Purpose:
- identify operator;
- establish session.

## Screen 02 — Home

Actions:
- Start Field Test
- Continue Active Test
- History
- Verify Evidence
- Settings

## Screen 03 — Setup

Fields:
- operator;
- case/event;
- assay/profile;
- location status;
- capture mode.

## Screen 04 — Capture

Elements:
- camera;
- reference-card outline;
- reaction-zone guide;
- adaptive warnings.

## Screen 05 — Check

Show:
- blur;
- exposure;
- glare;
- card;
- calibration;
- ROI;
- overall readiness.

## Screen 06 — Analysis

Show:
- corrected image;
- reference patches;
- reaction ROI;
- colour-space explanation.

## Screen 07 — Result

Show:
- presumptive outcome;
- inconclusive/invalid handling;
- explanation;
- laboratory-confirmation notice.

## Screen 08 — Evidence Passport

Show four sections and seal/sign action.

## Screen 09 — Timeline

Show ordered event history.

## Screen 10 — Export / Lab Referral

Allow JSON/HTML export.

## Screen 11 — History

Provide filtering/search.

## Screen 12 — Verify Evidence

Verify:
- digest;
- signature;
- chain.

## Screen 13 — QA / Demo Mode

Provide:
- synthetic scenarios;
- benchmark results;
- tamper demonstration.

---

# 33. UX Requirements

## Field Mode

Must be:

- high contrast;
- night-readable;
- sparse;
- calm;
- obvious about system state;
- obvious about uncertainty;
- minimal in typing;
- large in primary controls.

## One Primary Action Per Screen

The interface should reduce cognitive load during capture.

## Status Communication

Never communicate state through colour alone.

Every state should use:

**icon + text + state**

Examples:

- [✓] REFERENCE CARD DETECTED
- [✓] MEASUREMENT READY
- [!] INCONCLUSIVE
- [✕] CAPTURE INVALID

## Avoid

- excessive animations;
- gamification;
- exaggerated "AI magic";
- fake confidence meters;
- ambiguous colours without textual labels.

---

# 34. Data Requirements

## 34. Data Requirements

REACTRA shall use explicit, versioned schemas. Analytical, provenance, procedural and cryptographic fields must not be hidden in unstructured notes when they affect interpretation or verification.

## 34.1 TABLE: test_sessions

```text
id
case_id
event_id
operator_id
field_officer_name
field_officer_designation
police_station_jurisdiction
assay_profile_id
assay_profile_version
status
capture_mode
created_at_utc
updated_at_utc
gps_status
latitude
longitude
location_accuracy
sync_state
device_enrollment_id
signing_key_fingerprint
```

## 34.2 TABLE: reaction_timing

```text
test_id
reaction_started_at_utc
capture_timestamp_utc
capture_elapsed_seconds
timer_source
kinetic_window_status
t_min_seconds_snapshot
t_max_seconds_snapshot
reaction_start_event_id
```

Rules:

- `capture_elapsed_seconds` is calculated from a monotonic clock for `LIVE_CAMERA`.
- `t_min_seconds_snapshot` and `t_max_seconds_snapshot` freeze the profile parameters used for the test.
- Any timing-dependent test outside the window is non-classifiable.
- Imported images remain explicitly labelled and retain their timing provenance.

## 34.3 TABLE: measurement_results

```text
test_id
card_detection_confidence
calibration_residual
blur_metric
exposure_metric
glare_metric
roi_pixel_count
specular_rejected_pixel_count
specular_rejected_fraction
roi_sampling_method
roi_kmeans_k
selected_cluster_id
selected_cluster_area_fraction
reaction_lab_l
reaction_lab_a
reaction_lab_b
quality_status
result
class_distance_1
class_distance_2
decision_margin
classifier_invocation_count
algorithm_version
model_version
```

## 34.4 TABLE: assay_profiles

```text
profile_id
profile_name
profile_version
status
manufacturer_or_source
reference_card_version
threshold_configuration
calibration_targets
classifier_configuration
t_min_seconds
t_max_seconds
kinetic_window_required
reaction_start_definition
reaction_roi_definition
roi_sampling_method
roi_kmeans_k
roi_min_valid_pixels
specular_Lstar_threshold
specular_saturation_threshold
profile_effective_from_utc
profile_effective_until_utc
profile_snapshot_hash
```

## 34.5 TABLE: procedural_context

```text
test_id
search_context_type
authorization_reference
panchnama_memo_ref_no
panch_witness_1_name
panch_witness_2_name
procedural_safeguard_status
section_50_status
section_50_choice_recorded
gazetted_officer_or_magistrate_reference
inventory_ref_no
section_52a_reference
sample_identifier
seal_identifier
sample_drawal_status
magistrate_certification_status
section_57_report_ref_no
section_57_report_status
officer_notes
```

All statutory fields are nullable and/or have explicit applicability states. They are evidence-reference fields, not legal determinations.

## 34.6 TABLE: evidence_records

```text
test_id
image_path_or_secure_image_reference
image_sha256
canonical_record_json
record_digest
signature
public_key_fingerprint
signing_key_fingerprint
device_enrollment_id
trust_registry_version
signing_device_authorization_status
previous_record_hash
integrity_status
```

## 34.7 TABLE: audit_events

```text
event_id
test_id
event_type
event_timestamp_utc
event_payload_hash
previous_event_hash
actor_id
device_enrollment_id
```

## 34.8 TABLE: device_enrollments

```text
device_enrollment_id
device_platform
device_attestation_id
public_key_fingerprint
issuer_id
registry_version
enrolled_at_utc
valid_from_utc
valid_until_utc
status
revoked_at_utc
revocation_reason
enrollment_record_hash
```

## 34.9 TABLE: trusted_key_registry

```text
registry_version
issuer_id
issued_at_utc
registry_payload_hash
registry_signature
authority_key_fingerprint
```

The registry itself must be signed by the issuing authority and verified before device entries are trusted.

## 34.10 Canonical record snapshot

Every sealed test must preserve the exact analytical/provenance snapshot used for interpretation, including:

- kinetic parameters and elapsed time;
- ROI sampling configuration and measured colour;
- profile/reference-card/algorithm versions;
- procedural reference metadata;
- cryptographic identity.

Historical records must remain verifiable after software/profile upgrades.

# 35. Session State Machine

Required states:

- DRAFT
- CAPTURED
- QUALITY_CHECKING
- VALIDATION_FAILED
- READY_FOR_CLASSIFICATION
- CLASSIFIED
- REVIEW_REQUIRED
- REFERRAL_REQUIRED
- EVIDENCE_SEALED
- COMPLETED

Key transitions:

**DRAFT → CAPTURED → QUALITY_CHECKING**

Quality check:
- failure → VALIDATION_FAILED
- pass → READY_FOR_CLASSIFICATION

Classification:
- clear → CLASSIFIED
- ambiguous → REVIEW_REQUIRED

Classified:
- → EVIDENCE_SEALED

Review:
- → REFERRAL_REQUIRED
- or → EVIDENCE_SEALED

Evidence:
- → COMPLETED

The active session must survive navigation and, where technically supported, application refresh.

---

# 36. Security Requirements

## 36. Security Requirements

REACTRA must defend against:

### T1 — Image Tampering
Use image SHA-256 in the signed evidence record.

### T2 — Result Tampering
Use canonical record + Ed25519 signature.

### T3 — Metric Tampering
Include timing, ROI, measurement and classification metrics in the signed preimage.

### T4 — Record Deletion
Use a backward-linking chain and exported evidence envelopes.

### T5 — Reordering
Verify chain sequence.

### T6 — Profile Version Reinterpretation
Freeze profile version, reference-card version, algorithm version, kinetic-window values and ROI-sampling configuration.

### T7 — Imported Image Misrepresentation
Persist immutable capture mode.

### T8 — GPS Fabrication
Persist GPS status and location provenance.

### T9 — Poor Image Causing Bad Result
Apply quality gate before classifier.

### T10 — Unsupported Assay
No profile = no classification.

### T11 — Out-of-Window Reaction
Persist reaction start, elapsed time and `t_min`/`t_max`; block classification outside the valid window.

### T12 — Private Key Compromise
MVP:
- OS-restricted private key;
- private key never exported in evidence envelopes;
- explicit device-enrollment record.

Production:
- Android Keystore/hardware-backed key where available;
- iOS Secure Enclave where available;
- TPM/HSM-backed enterprise deployment where supported.

### T13 — Rogue/Reinstalled Device

A mathematically valid signature is not enough.

Verification must also prove that the signing key belongs to an enrolled and non-revoked device in the authority-signed trusted registry.

A new installation must not self-authorize a new key.

### T14 — Trusted Registry Tampering

`trusted_public_keys.json` must have its own authority signature.

Verification must fail if:

- registry signature is invalid;
- issuer trust anchor is unknown;
- device key is absent;
- device key is revoked.

### T15 — Device Attestation Failure

Where platform attestation is available, record:

- attestation ID;
- attestation state;
- hardware-backed status where provided.

If the hackathon cannot access real platform attestation, the value must be labelled simulated/demo-only.

### T16 — Procedural Metadata Tampering

Procedural references are signed as record data. Modifying a panchnama reference, witness name, station jurisdiction, sample ID or seal ID after sealing must invalidate verification.

### T17 — Central API Abuse

For any future central synchronization/control plane:

- per-device/user/IP rate limits;
- payload-size and concurrent-upload limits;
- idempotency keys;
- replay detection;
- exponential-backoff retries;
- circuit breakers.

### T18 — Unauthorized Access

Production RBAC roles:

- `FIELD_OPERATOR`
- `SUPERVISOR`
- `FORENSIC_REVIEWER`
- `EVIDENCE_AUDITOR`
- `SYSTEM_ADMIN`

Least privilege is mandatory.

`SYSTEM_ADMIN` must not silently edit a sealed evidence record.

### T19 — Audit Log Removal

Critical administrative events must be captured in a separate append-only administrative audit stream in production.

### T20 — Device Compromise

Cryptography cannot prove that the camera sensor itself was truthful before capture or that the operating system was uncompromised.

# 37. Functional Requirements

### FR-000A — Reaction Timer
The system shall provide an explicit `START REACTION` action tied to the protocol-defined reaction start event.

### FR-000B — Kinetic Window Gate
For timing-dependent profiles, the system shall reject captures outside `[t_min_seconds, t_max_seconds]` and set `INVALID_CAPTURE: OUTSIDE_VALID_KINETIC_WINDOW`.

### FR-000C — Robust ROI Sampling
The system shall reject specular pixels, spatially cluster valid ROI pixels, select the dominant reaction cluster, and calculate its median CIE L*a*b* vector.

### FR-000D — Device Enrollment
The system shall distinguish a mathematically valid signature from an authorized signing device.

### FR-000E — Trusted Registry Verification
The verifier shall validate the authority signature on the trusted device registry before accepting a device as authorized.

## FR-001 — Session Creation

The system shall create a unique test session ID automatically.

## FR-002 — Operator Identification

Operator ID shall be required before field analysis.

## FR-003 — Profile Selection

System shall require a configured assay profile before classification.

## FR-004 — Capture Modes

System shall distinguish LIVE_CAMERA and IMPORTED_IMAGE.

## FR-005 — Capture Guidance

System shall visually guide reference-card and reaction-ROI framing.

## FR-006 — Quality Analysis

System shall evaluate blur, exposure, glare, card geometry, calibration and ROI.

## FR-007 — Hard Quality Blocking

System shall prevent classifier execution following hard quality failure.

## FR-008 — Calibration

System shall transform the captured colour using the configured reference-card calibration process.

## FR-009 — Explainable Analysis

System shall expose measured colour and relevant distance/margin metrics.

## FR-010 — Four-State Result

System shall support positive, negative, inconclusive and invalid capture states.

## FR-011 — Unsupported Profile

System shall prevent classification if no suitable assay profile exists.

## FR-012 — Result Disclaimer

Every presumptive result shall display the laboratory-confirmation requirement.

## FR-013 — Evidence Sealing

System shall generate a signed evidence record.

## FR-014 — Hash Chain

System shall append valid records to the local backward-linking chain.

## FR-015 — Verification

System shall independently verify digest, signature and chain.

## FR-016 — Timeline

System shall display chronological test events.

## FR-017 — Search

System shall provide searchable historical records.

## FR-018 — Lab Referral

System shall generate JSON and HTML laboratory referral packets.

## FR-019 — Offline Operation

Core workflow shall function without internet.

## FR-020 — Sync Status

System shall clearly distinguish local, pending, synced and failed synchronization states.

---

# 38. Non-Functional Requirements

## 38. Non-Functional Requirements

## 38.1 Scientific / Measurement Requirements

### NFR-001 — Hard-Gate Safety
A hard-failing image must never be classified.

### NFR-002 — Kinetic Window Integrity
For timing-dependent profiles, captures before `t_min` or after `t_max` must be rejected as:

`INVALID_CAPTURE: OUTSIDE_VALID_KINETIC_WINDOW`

### NFR-003 — Robust ROI Sampling
The classifier must use the configured reflection-rejection + spatial-clustering + median-Lab sampling method rather than a naive all-pixel arithmetic mean.

### NFR-004 — Explainability
Operators/reviewers must be able to see the basis of the presumptive interpretation.

## 38.2 Integrity / Provenance Requirements

### NFR-005 — Integrity
Any material modification to signed record content should fail verification.

### NFR-006 — Device Authorization
A valid Ed25519 signature from an unregistered/revoked key must still be rejected as unauthorized.

### NFR-007 — Provenance
Source/capture mode, timing source and location status must be truthful.

### NFR-008 — Auditability
Important analytical, procedural and administrative state transitions must be traceable.

## 38.3 Field Resilience

### NFR-009 — Offline Core
Loss of network must not prevent core field operation.

### NFR-010 — Graceful Degradation
When optional central services are unavailable:

- continue local capture/analysis/signing;
- queue synchronization;
- expose `LOCAL_ONLY` / `PENDING_SYNC`;
- allow local evidence verification;
- switch central history to read-only when writes are unavailable;
- never silently drop records.

### NFR-011 — Recovery
Interrupted sessions must recover from local persisted state where technically supported.

## 38.4 Performance — Hackathon MVP

The MVP is a single-device/offline prototype and is not a distributed high-load system.

On designated reference hardware:

- P95 still-image analysis: **≤ 2 seconds** after capture ingestion;
- P99 still-image analysis: **≤ 5 seconds**;
- evidence sealing: **≤ 1 second** excluding user interaction;
- local history lookup: **≤ 250 ms P95** for a representative prototype dataset;
- non-processing UI action feedback: **≤ 200 ms** target.

These are engineering usability targets, not forensic validity standards.

## 38.5 Production-Scale Performance Envelope

If deployed as a multi-device field system, the central services must be capacity-tested for at least **10× the measured pilot peak load** without architectural redesign.

Define:

- `pilot_peak_concurrent_sync_clients`;
- `pilot_peak_tps`;
- `target_concurrent_sync_clients = 10 × pilot_peak_concurrent_sync_clients`;
- `target_peak_tps = 10 × pilot_peak_tps`.

For the optional central API/control plane:

- **P95 < 200 ms** for lightweight metadata/read/write requests under target load;
- **P99 < 500 ms** for those requests under target load;
- resource-intensive processing must not block synchronous API responses.

These targets apply to the central control/sync plane, not the local image-analysis path.

## 38.6 Availability / SLA

### Offline field core
Critical field measurement is independent of central availability.

### Production central services
Target monthly availability: **99.9%** for synchronization/control-plane services.

A central outage must not make already-captured local evidence inaccessible.

## 38.7 Throughput / Concurrency

Production load testing must cover:

- 10× pilot peak concurrent sync clients;
- 10× pilot peak TPS;
- burst traffic when devices reconnect after an outage;
- simultaneous evidence uploads;
- synchronization retries and duplicates.

All synchronization is idempotent.

## 38.8 Graceful Degradation

When dependencies fail:

1. local field operation continues;
2. central sync queues envelopes;
3. non-critical analytics pause;
4. cached/read-only history remains available;
5. retries use exponential backoff;
6. circuit breakers prevent cascading downstream failure;
7. sync state is visible to the operator.

## 38.9 Caching / Data Access

MVP:
- local SQLite;
- indexed history queries;
- on-device cached profile/trust-registry data.

Production:
- Redis or equivalent may cache frequently-read non-authoritative metadata;
- cache must never become the authority for sealed evidence;
- evidence verification reads canonical source data.

## 38.10 Asynchronous Processing

Production central jobs that may be expensive or long-running shall use background workers:

- synchronization reconciliation;
- bulk report generation;
- archive jobs;
- analytics;
- notifications;
- large exports.

Each job is:
- identified by `job_id`;
- idempotent;
- retryable;
- observable.

## 38.11 Database Scalability

MVP:
- SQLite per device;
- versioned migrations;
- indexes for required filters.

Production:
- PostgreSQL or equivalent transactional database;
- primary/read replicas where justified by read volume;
- partition large audit/event tables by time and/or jurisdiction as growth requires;
- immutable content-addressed object storage for large images;
- do not delete sealed records merely for database-size control.

## 38.12 Rate Limiting / Throttling

For future central APIs, support configurable:

- per-device limits;
- per-user limits;
- per-IP/network limits;
- concurrent-upload limits;
- payload-size limits.

Initial engineering defaults:

- **60 requests/minute/device** for normal control/metadata APIs;
- short burst up to **2×** steady-state rate;
- evidence-upload endpoints use separate size/concurrency limits;
- synchronization requests use idempotency keys.

These are initial engineering defaults and require load testing before production deployment.

## 38.13 Access Control

Production RBAC must enforce:

- Field Operator: create/capture/seal authorized test events;
- Supervisor: review team records and manage authorized operational settings;
- Forensic Reviewer: inspect analytical/provenance data;
- Evidence Auditor: verify/export evidence;
- System Administrator: manage users/devices/configuration but not silently alter sealed records.

Critical actions require audit logging.

## 38.14 Privacy / Regulatory Readiness

The prototype is India-focused and offline-first.

Production deployments must perform a deployment-specific privacy assessment under applicable Indian privacy/data-protection requirements, including the Digital Personal Data Protection Act, 2023 and applicable rules/provisions as they come into force. International deployment requires jurisdiction-specific review such as GDPR where applicable.

Central design should support:

- data minimization;
- role-based access;
- encryption at rest/in transit where central services exist;
- configurable retention;
- India-region storage where required by deployment policy;
- auditable retention/deletion operations where legally permitted.

## 38.15 Observability

Production central services shall expose:

### System health metrics
- API request count;
- P50/P95/P99 latency;
- 4xx/5xx error rate;
- queue depth;
- worker utilization;
- CPU/memory saturation;
- database connection-pool saturation;
- cache hit/miss ratio;
- synchronization backlog;
- evidence verification failures;
- device-key authorization failures.

### Product metrics
- tests initiated;
- quality-gate failure rate;
- recapture rate;
- inconclusive rate;
- unsupported-profile rate;
- offline queue age;
- laboratory-referral generation count;
- verification-failure count.

Synthetic/demo traffic must be tagged separately.

## 38.16 Alerting

### P1 Critical
- central availability below target;
- widespread signature verification failures;
- trusted registry invalid;
- evidence-sync corruption.

### P2 High
- sustained P95/P99 latency breach;
- queue depth above threshold;
- repeated sync failures;
- database saturation.

### P3 Operational
- elevated recapture rate;
- profile-loading failures;
- client-version mismatch;
- repeated authorization failures.

Every production alert must map to an incident runbook.

## 38.17 Feature Flags / Progressive Delivery

Production releases shall use:

- versioned feature flags;
- canary/percentage rollout where appropriate;
- auditable flag changes;
- immediate rollback.

Feature flags must never permit bypass of:
- hard quality gates;
- kinetic timing gates;
- evidence signing;
- trust-registry verification;
- safety disclosures.

## 38.18 Maintainability

Scientific, evidence, database, security and UI modules must remain separated.

The prototype must explicitly preserve contracts that allow migration from Streamlit/local execution to a native field client and optional service-backed production architecture.

# 39. Technology Requirements

## 39. Technology Requirements

## 39.1 Hackathon MVP Architecture

The MVP is intentionally local and offline-first:

- Python 3.11
- Streamlit
- OpenCV
- NumPy
- Pillow
- SQLite
- cryptography package
- local JSON/HTML packaging

Streamlit is the **functional prototype UI**, not a claim that Streamlit itself is the final production mobile architecture.

The MVP does not require:

- cloud infrastructure;
- Kubernetes;
- Redis;
- external message queues;
- remote APIs;
- blockchain;
- or central database availability.

## 39.2 Production Field Client

P1 target:

- native Android/iOS application or secure native shell;
- native camera controls;
- native GPS/location services;
- hardware-backed key storage;
- local encrypted persistence;
- secure background synchronization.

The production client preserves the same domain/service contracts as the MVP so the analytical/evidence layers can be reused.

## 39.3 Production Central Plane

Only where institutional deployment requires centralized services:

- API gateway;
- authentication/authorization;
- synchronization service;
- PostgreSQL primary and read replicas as required;
- immutable/content-addressed object storage for large media;
- Redis/equivalent cache;
- background queue and worker pool;
- observability/metrics;
- signed configuration and trusted-device registry.

## 39.4 API Versioning

Central APIs use explicit versions such as:

`/api/v1/...`

Breaking changes require a new API version.

## 39.5 Schema Migration

All persistent schemas carry a schema version.

SQLite migrations must be:

- numbered;
- deterministic;
- forward-tested;
- recovery-documented.

Production migrations should use additive expand/contract patterns where needed for zero-downtime upgrades.

## 39.6 Data Access Policy

- UI never performs direct SQL.
- Repository/service layer owns data access.
- Evidence verification always uses canonical source data, not a cache-only copy.
- Caches are disposable and never authoritative.

## 39.7 Background Job Contract

Every production asynchronous job requires:

```text
job_id
job_type
idempotency_key
status
attempt_count
created_at_utc
started_at_utc
completed_at_utc
failure_reason
```

# 40. Synthetic Prototype Data Policy

The hackathon prototype should use synthetic images.

Synthetic data may model:

- positive/negative/inconclusive colour regions;
- perspective variation;
- blur;
- exposure changes;
- glare;
- card misalignment;
- ambiguous colours.

The prototype must never claim:

> "100% real-world accuracy."

Correct framing:

> "REACTRA achieved X on a controlled synthetic benchmark with known ground truth. This does not estimate field performance."

Future physical validation requires authorised materials, controlled testing, appropriate institutional approval and documented calibration.

---

# 41. Prototype Benchmarking Requirements

The prototype may report:

- controlled synthetic precision;
- controlled synthetic recall;
- controlled synthetic F1;
- scenario-level quality-gate performance.

Every benchmark must include:

- dataset composition;
- synthetic/real status;
- sample count;
- assay profile;
- camera/device conditions where relevant;
- known limitations.

The critical engineering acceptance test is:

> **No hard-fail image reaches the classifier.**

---

# 42. MVP Scope

## Must Have

1. REACTRA branding everywhere.
2. Field-user UX.
3. Adaptive Capture Guard.
4. Four-state outcome model.
5. Strict classifier blocking on hard measurement failure.
6. Profile-driven configuration.
7. Reliability Passport.
8. Evidence Timeline.
9. Cryptographic verification screen.
10. Laboratory Referral Packet.

## Should Have

11. Offline indicator.
12. GPS provenance indicator.
13. Case/Event ID.
14. Kit lot/expiry metadata.
15. Unknown-profile workflow.
16. Multilingual-ready UI.

## Future

17. Native camera/GPS.
18. Hardware-backed keys.
19. Temporal reaction analysis.
20. Authorized physical validation.

---

# 43. Product Differentiation

The product must not claim that smartphone scanning, reporting, GPS, or local storage are unique capabilities.

REACTRA differentiates through the combination of:

1. **Measurement validity before classification**
2. **Adaptive Capture Guard**
3. **Explainable presumptive interpretation**
4. **Four-state outcome model**
5. **Evidence Reliability Passport**
6. **Cryptographic provenance**
7. **Version-aware assay profiles**
8. **Evidence Timeline**
9. **Laboratory Handoff**
10. **India-context field workflow**
11. **Offline-first honest metadata**
12. **Operator decision support instead of autonomous enforcement**

### Competitive message

> REACTRA does not simply recognize a colour. It first verifies that the measurement is usable, explains a presumptive result only for the exact configured test profile, and seals the complete event into a verifiable evidence timeline.

### Strongest innovation statement

> The core innovation is the integration of measurement validity, explainable presumptive interpretation, and cryptographic evidence provenance into one offline field workflow, with explicit handling of uncertainty and failure.

### One thing REACTRA refuses to do

> **Guess.**

---

# 44. Product Success Metrics

The MVP should prioritize measurable engineering behaviour rather than unsupported field-performance claims.

## Success Metric A — Quality-Gate Safety

**100% of configured hard-fail demo captures are blocked from classification.**

This is a prototype acceptance target, not a field-validation claim.

## Success Metric B — Provenance Completeness

For a valid completed demo record, all required provenance fields should be present and truthfully labelled.

## Success Metric B2 — Kinetic Gate Safety

For timing-dependent demo profiles, 100% of captures outside the configured kinetic window are blocked from classification.

## Success Metric B3 — Robust ROI Sampling

Every classified demo record must contain:
- specular rejection statistics;
- selected cluster metadata;
- median reaction L*a*b* values.


## Success Metric C — Cryptographic Verification

Tampering with:
- result,
- operator,
- analytical metric,
- image,

must cause verification failure.

## Success Metric D — Offline Completion

A complete demo session must be executable without network access.

## Success Metric E — Uncertainty Handling

Ambiguous and unsupported cases must not be forced into positive/negative outcomes.

## Success Metric F — Recovery

An active session should be recoverable after navigation and supported application refresh/reload conditions.

---

# 45. Required Demo Scenarios

## Demo 1 — Good Capture
Show:
- successful quality gate;
- presumptive interpretation;
- evidence seal.

## Demo 2 — Night / Low Light
Show:
- low-light warning;
- operator instruction;
- retake;
- calibrated successful capture.

## Demo 3 — Glare
Show:
- glare detection;
- classification blocked;
- corrective instruction.

## Demo 4 — Motion Blur
Show:
- blur metric;
- RECAPTURE REQUIRED;
- classifier invocation = 0.

## Demo 5 — Ambiguous Reaction
Show:
- valid measurement;
- INCONCLUSIVE;
- REVIEW;
- laboratory referral.

## Demo 6 — Unknown Profile
Show:
- no matching assay profile;
- no forced identity;
- referral/review path.

## Demo 7 — Tampered Record
Modify:
- result or operator or metric.

Show:
- digest/signature failure.

## Demo 8 — Deleted Record
Delete an intermediate chain record.

Show:
- chain discontinuity.

## Demo 9 — Imported Image
Show:
- IMPORTED_IMAGE label.

## Demo 10 — GPS Unavailable
Show:
- GPS: UNAVAILABLE.

## Demo 11 — Offline Mode
Disconnect network and complete:
- capture;
- analysis;
- evidence seal;
- search.

## Demo 12 — Evidence Timeline
Show ordered chain-of-events.

## Demo 13 — Kinetic Window: Too Early
Start reaction timer and attempt capture before `t_min`.
Show:
- WAITING FOR VALID WINDOW;
- capture blocked or marked invalid;
- classifier invocation count = 0.

## Demo 14 — Kinetic Window: Too Late
Allow timer to pass `t_max` and attempt capture.
Show:
- WINDOW EXPIRED;
- `INVALID_CAPTURE: OUTSIDE_VALID_KINETIC_WINDOW`;
- classification blocked.

## Demo 15 — Reflection-Rich Liquid ROI
Use synthetic bubbles/glints/uneven liquid.
Show:
- specular-pixel rejection;
- cluster segmentation;
- median-Lab extraction;
- explainable reaction ROI.

## Demo 16 — Unauthorized Signing Key
Replace the signing key in a test envelope without changing the authority-signed registry.
Show:
- mathematical signature validity is not enough;
- signing-device authorization fails;
- evidence is marked untrusted/unauthorized.

## Demo 17 — Procedural Reference Metadata
Show:
- officer designation;
- station jurisdiction;
- panchnama reference;
- panch-witness fields;
- sample/seal references;
- recordkeeping-only notice.

## Demo 18 — Central Service Outage
Simulate central service failure.
Show:
- local evidence capture continues;
- sync queue becomes `PENDING_SYNC`;
- no data loss;
- retry after service restoration.

---

# 46. Primary Judge Demo

## 0:00–0:25 — Problem

Message:

> The existing field kit produces a colour reaction. The measurement conditions and manual interpretation around that reaction create subjectivity, while paper/manual documentation creates traceability gaps.

## 0:25–0:55 — Setup

Show:
- operator;
- assay profile;
- location status.

## 0:55–1:35 — Adaptive Capture

Show:
- poor/night capture;
- Adaptive Capture Guard;
- invalid capture;
- corrective instruction;
- retake.

## 1:35–2:05 — Measurement

Show:
- reference card;
- calibration;
- quality gate;
- ROI overlay.

## 2:05–2:35 — Result

Show:
- presumptive result;
- explanation;
- laboratory-confirmation banner.

## 2:35–3:10 — Evidence

Show:
- Reliability Passport;
- Evidence Integrity: VERIFIED;
- hash;
- signature;
- chain.

## 3:10–3:35 — Tamper Demonstration

Modify exported JSON and show verification failure.

## 3:35–4:00 — Handoff

Show:
- evidence timeline;
- laboratory referral packet.

### Final product line

> **REACTRA does not replace the field kit or the forensic laboratory. It makes the field measurement more standardized, the uncertainty visible, and the digital record verifiable.**

---

# 47. Risks and Mitigations

## R1 — Overclaiming chemical identification

**Risk:** Judges/users interpret the prototype as a definitive drug detector.

**Mitigation:** Mandatory presumptive wording and laboratory-confirmation banner.

## R2 — Poor image produces false classification

**Risk:** Blur/exposure/glare reduces reliability.

**Mitigation:** Adaptive Capture Guard + hard quality gate.

## R3 — Unsupported assay

**Risk:** Generic model is applied to an unrelated kit.

**Mitigation:** Profile-driven architecture + no-profile/no-classification rule.

## R4 — Fake provenance

**Risk:** Demo coordinates or imported images appear real.

**Mitigation:** explicit GPS/source/capture-mode labels.

## R5 — Evidence tampering

**Risk:** Stored records are altered.

**Mitigation:** SHA-256 + Ed25519 + hash chain + independent verification.

## R6 — Offline failure

**Risk:** Core features stop without network.

**Mitigation:** local processing/storage/signing and explicit sync states.

## R7 — Synthetic metrics misunderstood

**Risk:** prototype benchmark presented as field accuracy.

**Mitigation:** visible controlled-synthetic benchmark labels and documentation.

## R8 — UI becomes too technical

**Risk:** field operator sees developer diagnostics instead of actionable guidance.

**Mitigation:** separate Field Mode from QA/Developer Mode.

---

# 48. Release Plan

## Release 0 — Hackathon MVP

Deliver:

- field workflow;
- reference card;
- quality gate;
- calibrated analysis;
- four states;
- explanation;
- Reliability Passport;
- signed evidence;
- local chain;
- searchable history;
- lab referral;
- synthetic demos;
- offline operation.

## Release 1 — Field Hardening

Add:

- native camera;
- GPS;
- secure hardware-backed keys;
- device-specific camera profiling;
- role-based authentication;
- kit lot/expiry;
- multilingual field UI;
- authorized user testing.

## Release 2 — Research

Explore:

- reaction video;
- temporal consistency;
- improved optical processing;
- controlled physical assay dataset.

## Release 3 — Institutional Integration

Explore only through authorized interfaces:

- laboratory/LIMS integration;
- evidence-system integration;
- central synchronization;
- supervisor dashboards.

---

# 49. Acceptance Criteria

A release is accepted only when a trained prototype user can:

### AC-01
Start a new test and obtain a unique test ID.

### AC-02
Identify the operator and configured profile.

### AC-03
Capture an image with reference card guidance.

### AC-04
Receive actionable feedback for poor captures.

### AC-05
See classifier execution blocked for hard quality failures.

### AC-06
Obtain a presumptive interpretation only for a supported configured profile.

### AC-07
Receive INCONCLUSIVE rather than forced classification for ambiguous cases.

### AC-08
Receive INVALID CAPTURE for unusable images.

### AC-09
See which colour region was measured.

### AC-10
See the exact assay/profile/reference-card/algorithm versions used.

### AC-11
See the laboratory-confirmation warning.

### AC-12
Seal a complete evidence record.

### AC-13
Verify the record independently.

### AC-14
Detect tampering with result/operator/metric/image.

### AC-15
Detect deletion/reordering in the chain.

### AC-16
Search and reopen historical records.

### AC-17
View the chronological evidence timeline.

### AC-18
Generate a laboratory referral packet.

### AC-19
Complete core operation without internet.

### AC-20
Truthfully display unavailable GPS or imported-image provenance.

### AC-21
Never produce an automated legal conclusion.

### AC-22
Never produce a fake laboratory result.

---

# 50. Anti-Patterns

Do NOT build:

- Upload photo → chatbot → drug name
- a single "AI confidence" score
- a classifier that accepts blurry/overexposed inputs
- a generic model with no assay profile
- positive/negative only
- fake GPS
- fake laboratory certificates
- cloud-required core operation
- blockchain used only for marketing
- unsupported forensic-certification claims
- hard-coded results hidden behind "AI"

---

# 51. Implementation Architecture

## 51. Implementation Architecture

Recommended modular structure:

```text
reactra/
  ui/
    pages/
    components/
    field_mode/
    qa_mode/

  session/
    state_machine.py
    manager.py
    recovery.py

  vision/
    capture.py
    card_detector.py
    calibration.py
    quality_gate.py
    roi_detector.py
    exposure.py
    glare.py
    temporal_gate.py
    roi_sampler.py

  profiles/
    loader.py
    validator.py
    schemas/
    profiles/

  classification/
    predictor.py
    thresholds.py
    evaluation.py

  evidence/
    canonical.py
    hashing.py
    signing.py
    chain.py
    verifier.py
    envelope.py
    timeline.py

  database/
    connection.py
    schema.py
    repository.py
    migrations.py

  referral/
    lab_packet.py

  metadata/
    location.py
    device.py
    timing.py

  security/
    key_store.py
    enrollment.py
    attestation.py
    trusted_registry.py
    access.py

  demo/
    scenarios.py
    fixtures.py

  app.py
```

## 51.1 UI / Service Separation Rule

UI may display data.

UI must not own:

- scientific algorithms;
- SQL;
- cryptographic primitives;
- statutory decision logic.

## 51.2 Scale-Aware Production Architecture

The local field client remains the source of operational resilience.

```text
                   AUTHORIZED FIELD DEVICES
          ┌───────────────────────────────────────┐
          │ camera + local CV + SQLite            │
          │ timer + signing + offline queue       │
          └───────────────────┬───────────────────┘
                              │ intermittent sync
                              ▼
                    ┌─────────────────────────┐
                    │ API GATEWAY / AUTH      │
                    │ rate limit/idempotency  │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼────────────────────┐
             ▼                   ▼                    ▼
      Sync Service      Profile/Device Registry    Read API
             │                   │                    │
             ▼                   │              Cache Layer
        Job Queue               │                    │
             │                   ▼                    │
             ▼            PostgreSQL Primary ◄──────┘
        Worker Pool              │
                                 ├── Read Replicas
                                 │
                                 ▼
                          Audit / Evidence Store
                                 │
                                 ▼
                          Immutable Object Store
```

This is a future institutional architecture, not an MVP requirement.

## 51.3 Scaling Rules

- local field processing continues if the central plane is unavailable;
- synchronization is idempotent;
- replayed envelopes do not create duplicate evidence records;
- profile and trusted-device registries are versioned and signed;
- read-heavy operations may use cache/read replicas;
- successful central ingestion is reported only after transactional acceptance;
- large images use immutable content-addressed objects;
- background workers handle bulk exports, notifications, analytics and reconciliation;
- audit records are append-only.

## 51.4 Administrative Tooling

Production administration should support:

- device enrollment/revocation;
- trust-registry issuance;
- profile lifecycle management;
- role/user management;
- key rotation;
- configuration versioning;
- audit inspection;
- synchronization backlog;
- evidence verification;
- incident diagnostics.

Administrative tooling must not silently mutate sealed evidence.

## 51.5 Migration / Compatibility

Every client/server release declares:

- `app_version`;
- `schema_version`;
- `api_version`;
- `profile_schema_version`;
- `evidence_format_version`.

Sealed evidence remains independently verifiable after upgrades.

Historical records must be opened using stored version metadata and must not be silently reinterpreted with newer algorithms/profiles.

# 52. Product Decision Log

## Decision 1
Use a field-evidence-companion positioning rather than "AI drug detector."

## Decision 2
Preserve the previous CIE Lab, hashing, signing, local database and evidence functions where they comply with V2.

## Decision 3
Make INVALID CAPTURE a first-class state.

## Decision 4
Treat measurement validity as a prerequisite for classification.

## Decision 5
Use profile/version provenance to prevent generic interpretation.

## Decision 6
Separate evidence integrity from classification.

## Decision 7
Support offline operation.

## Decision 8
Use synthetic data for the hackathon prototype.

## Decision 9
Do not claim automatic legal admissibility.

## Decision 10
Keep advanced kinetics and institutional integration outside the MVP.

---

# 53. Open Validation Items

The source specification identifies several areas that cannot be claimed as fully validated by the hackathon prototype and therefore remain validation items:

1. Real physical assay calibration.
2. Real reagent/chemical behaviour.
3. Camera sensor and lens variability.
4. Real-world lighting and environmental variation.
5. Cross-reactivity and adulterant effects.
6. Production thresholds for specific kits/devices.
7. Institutional/legal workflow integration.
8. Hardware-backed key storage.
9. Native camera/GPS integration.
10. Laboratory/LIMS integration.

These are product validation and deployment concerns, not reasons to overstate MVP capability.

---

# 54. Final Product Definition

REACTRA V2 is complete when a trained operator can:

1. begin a field-test session;
2. capture a test alongside a reference card;
3. receive immediate feedback when the image is unusable;
4. obtain a calibrated presumptive interpretation only when measurement conditions are acceptable;
5. see exactly what was measured;
6. see which assay/profile/version was used;
7. see the uncertainty and presumptive nature of the result;
8. seal the event into a digital evidence record;
9. independently verify cryptographic integrity;
10. search the event through an evidence timeline;
11. prepare a laboratory referral package;
12. operate the core workflow offline;

while REACTRA does not claim to determine final chemical identity, legal status, guilt, or laboratory confirmation.

---

# 55. Product North Star

> **Make every field-test event measurable, explainable, and verifiable — without pretending uncertainty does not exist.**

---

# Appendix A — Recommended Product Copy

## One Line

> **REACTRA turns a subjective field colour test into a standardized, explainable and verifiable digital evidence event.**

## Two Lines

> **We do not replace the field kit or the laboratory. We improve the layer in between: measurement quality, presumptive interpretation, operator guidance and evidence provenance.**

## Three-Part Story

**MEASURE**  
Standardize the visual observation.

**EXPLAIN**  
Show why the result was generated or withheld.

**PRESERVE**  
Seal the event into a verifiable digital record.

---

# Appendix B — Core Judge Answers

### Does this already exist?

Mobile presumptive-test products already exist. REACTRA does not claim smartphone scanning itself as novel.

The differentiator is the integration of:
- pre-classification measurement gating,
- operator-guided recapture,
- calibrated and explainable interpretation,
- four-state uncertainty handling,
- profile/version provenance,
- local cryptographic integrity,
- and a field-to-laboratory evidence lifecycle.

### How is REACTRA different from existing mobile presumptive-test products?

REACTRA focuses on the measurement-validity gate, operator guidance, transparent explanation, evidence provenance, integrity verification and complete event lifecycle rather than claiming basic smartphone reporting features as novel.

### Why not deep learning?

The MVP prioritizes controlled, inspectable and explainable behaviour in calibrated colour space. More complex models can be researched later after an adequately validated physical dataset exists.

### What if the capture is terrible?

REACTRA does not guess. The Adaptive Capture Guard blocks the measurement and tells the operator what to fix.

### What if the result is ambiguous?

INCONCLUSIVE. It is not forced into positive or negative.

### What if the kit is unsupported?

No matching profile means no automated classification. The event may still be documented and referred.

### Does a positive result prove illegal possession?

No. It is a presumptive field-test result for the configured assay. Legal status and final chemical identification remain outside REACTRA.

### Does the hash make the record automatically admissible?

No. Cryptographic mechanisms strengthen integrity and provenance; legal admissibility depends on applicable law, procedure, certification and judicial assessment.

### Why offline?

Core measurement and evidence preservation should not stop because cellular connectivity is unavailable.

### Why synthetic data?

For safety, legality and reproducibility during the prototype phase. Production validation requires authorized physical data.

---

# Appendix C — Legal / Regulatory Source Notes

This PRD treats Indian legal and procedural context as configurable recordkeeping support rather than an automated legal decision engine.

Primary source anchors reviewed for this revision:

- Narcotic Drugs and Psychotropic Substances Act, 1985 — Sections 43, 50, 52A and 57.
- Bharatiya Nagarik Suraksha Sanhita, 2023 — general search/seizure provisions relevant to witness and seizure-list documentation.
- Bharatiya Sakshya Adhiniyam, 2023 — current central evidence statute for electronic records.
- Digital Personal Data Protection Act, 2023 and Digital Personal Data Protection Rules, 2025 — privacy/readiness considerations for future deployments.

## Legal implementation disclaimer

These source notes provide product-design context. They do not constitute legal advice or certify that a particular deployment, search, seizure, record, witness configuration or electronic record is legally compliant or admissible.

# End of PRD
