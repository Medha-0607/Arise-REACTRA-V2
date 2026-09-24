# REACTRA V2 — API Contract Specification
**API Version**: `v1`  
**Base URL**: `/api/v1`  
**Protocol**: REST / JSON  

---

## 1. Overview & General Conventions

- All REST endpoints are strictly versioned under `/api/v1/`.
- All requests and responses use `application/json`.
- Standard HTTP status codes are enforced:
  - `200 OK`: Successful synchronous retrieval or state change.
  - `201 Created`: Resource successfully created.
  - `400 Bad Request`: Schema validation error, invalid state transition, image format error, or domain rule violation.
  - `404 Not Found`: Entity not found.
  - `422 Unprocessable Entity`: Semantic validation failure.
  - `500 Internal Server Error`: Unhandled server exception.

---

## 2. Implemented Endpoints (Phases 0, 2, 3)

### 2.1 System Health
- **Endpoint**: `GET /api/v1/health`
- **Description**: Returns basic service operational status, application version, and API version.
- **Response**: `200 OK`

### 2.2 Assay Profiles
- **Endpoint**: `GET /api/v1/profiles`
- **Description**: List all registered and active colorimetric assay profiles.
- **Response**: `200 OK`

### 2.3 Create Test Session
- **Endpoint**: `POST /api/v1/sessions`
- **Description**: Initialize a new authoritative test session in `DRAFT` state with bound procedural context, child record shells, and an initial audit event.
- **Response**: `201 Created`

### 2.4 Retrieve Test Session
- **Endpoint**: `GET /api/v1/sessions/{session_id}`
- **Description**: Retrieve complete authoritative session state, procedural context, shells, and chronological audit events.
- **Response**: `200 OK`

### 2.5 List Test Sessions
- **Endpoint**: `GET /api/v1/sessions`
- **Description**: Retrieve summary list of local test sessions.
- **Response**: `200 OK`

### 2.6 Request Session State Transition
- **Endpoint**: `POST /api/v1/sessions/{session_id}/transition`
- **Description**: Request a state transition governed strictly by the 10-state authoritative state machine.
- **Response**: `200 OK` or `400 Bad Request`

### 2.7 Retrieve Session Timeline
- **Endpoint**: `GET /api/v1/sessions/{session_id}/timeline`
- **Description**: Retrieve chronological audit trail and timeline of events.
- **Response**: `200 OK`

### 2.8 Execute Adaptive Capture Guard & Measurement Pipeline
- **Endpoint**: `POST /api/v1/sessions/{session_id}/measure`
- **Description**: Process visual field image capture through Adaptive Capture Guard (blur, exposure, glare, card localization, calibration) and extract calibrated reaction well CIE L\*a\*b\* coordinates.
- **Request Body**:
```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo...",
  "provenance": "LIVE_CAMERA",
  "elapsed_seconds": 30.0
}
```
- **Response (Quality Validation Passed)**: `200 OK`
```json
{
  "session_id": "SES-20260923-005037-B3C588",
  "session_status": "READY_FOR_CLASSIFICATION",
  "passed_quality_gates": true,
  "overall_quality_status": "READY",
  "quality_diagnostics": {
    "overall_status": "READY",
    "passed_all_hard_gates": true,
    "failure_reasons": [],
    "checks": {
      "blur": { "variance": 482.1, "threshold": 120.0, "passed": true, "explanation": "Focus sharpness acceptable." },
      "exposure": { "mean_luminance": 128.4, "underexposed_fraction": 0.01, "overexposed_fraction": 0.02, "dynamic_range": 220, "passed": true, "explanation": "Optimal illumination and dynamic range." },
      "glare": { "max_roi_glare_fraction": 0.008, "threshold": 0.05, "passed": true, "explanation": "Specular glare minimal.", "roi_glare_fractions": { "well_1": 0.008, "well_2": 0.0 } },
      "card_detection": { "detected": true, "confidence": 0.95, "aspect_ratio": 1.5, "area_fraction": 0.85, "reason": "Reference card quadrilateral successfully localized." },
      "alignment": { "passed": true, "skew_angle_deg": 2.1 },
      "calibration": { "passed": true, "mean_delta_e": 4.8, "threshold": 18.0, "explanation": "Color calibration successful.", "patch_count": 6, "patch_diagnostics": {} },
      "timing": { "compliance_status": "IN_WINDOW", "elapsed_seconds": 30.0, "target_window_seconds": 30, "min_window_seconds": 10, "max_window_seconds": 120, "passed": true, "explanation": "Reaction timing compliant." }
    }
  },
  "validated_measurement": {
    "measurement_id": "MSR-A38BC910",
    "session_id": "SES-20260923-005037-B3C588",
    "capture_id": "CAP-F48B77D2",
    "profile_id": "marquis-standard-v1",
    "profile_version": "1.0.0",
    "algorithm_version": "2.0.0",
    "reference_card_version": "ref-card-grid-3x2",
    "provenance": "LIVE_CAMERA",
    "measured_at": "2026-09-22T19:50:00Z",
    "timing_compliance": "IN_WINDOW",
    "elapsed_seconds": 30.0,
    "calibration_mean_delta_e": 4.8,
    "calibration_passed": true,
    "well_measurements": {
      "well_1": {
        "roi_id": "well_1",
        "name": "Primary Reaction Well",
        "bbox": [80, 180, 120, 120],
        "sampled_bbox": [88, 188, 104, 104],
        "valid_pixel_count": 142,
        "glare_pixel_count": 0,
        "raw_lab_median": [46.5, 34.2, -11.8],
        "calibrated_lab_median": [48.2, 36.5, -12.4],
        "calibrated_lab_trimmed_mean": [48.0, 36.3, -12.2],
        "lab_std_dev": [1.8, 1.2, 0.9],
        "is_valid": true,
        "rejection_reason": null
      }
    },
    "quality_diagnostics": { ... }
  }
}
```
- **Response (Quality Validation Failed)**: `200 OK`
```json
{
  "session_id": "SES-20260923-005037-B3C588",
  "session_status": "VALIDATION_FAILED",
  "passed_quality_gates": false,
  "overall_quality_status": "RECAPTURE",
  "quality_diagnostics": {
    "overall_status": "RECAPTURE",
    "passed_all_hard_gates": false,
    "failure_reasons": ["Image blur excessive: Excessive motion or focus blur detected (Laplacian variance: 22.4 < 120.0)."],
    "checks": { ... }
  },
  "validated_measurement": null
}
```
