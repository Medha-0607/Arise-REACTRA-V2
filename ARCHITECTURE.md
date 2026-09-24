# REACTRA V2 — Architecture Specification
**Product**: REACTRA — Reaction-Aware Field Testing & Verifiable Evidence  
**Problem Statement**: SIH26231  
**Architecture Version**: 2.0.0 (Phase 3 Scientific Pipeline & Adaptive Capture Guard Active)  

---

## 1. System Purpose & Core Boundaries

REACTRA is an offline-first field companion engineered to support law enforcement and field operators during presumptive colorimetric drug testing.

### 1.1 Non-Negotiable Boundaries
1. **Presumptive Scope Only**: REACTRA is NOT a chemical confirmation system and does NOT determine guilt, legal possession status, or laboratory confirmation.
2. **Deterministic Pre-Classifier Gating (PRD §10)**: Measurement validity is strictly separated from classification. If capture quality fails (`VALIDATION_FAILED`), the measurement is rejected immediately and cannot reach the classifier.
3. **Decoupled Classifier Input**: Raw images are NEVER passed directly to the classifier. The classifier receives exclusively a `ValidatedMeasurement` domain contract.
4. **No Fabrication**: Device metadata, location provenance, timestamps, and operator actions are strictly audited; no synthetic or placeholder data is ever presented as factual field evidence.
5. **Authoritative Backend & Persistence**: Frontend React/Zustand is strictly presentation and user interaction. All domain rules, session state machine transitions, and persistent storage reside authoritatively in the backend FastAPI service and SQLite database.
6. **Tamper-Evident Evidence**: Cryptographic envelopes (Ed25519 signatures, SHA-256 hash chains) guarantee tamper-evidence within the local trust model.

---

## 2. Multi-Tier Layered Architecture

```
+-------------------------------------------------------------+
|                     React Presentation Layer                |
|  (UI Components, Wizard Views, Zustand Cache/Presentation)   |
+-------------------------------------------------------------+
                              | (HTTP / REST JSON)
                              v
+-------------------------------------------------------------+
|                     FastAPI Routing Layer                   |
|              (/api/v1/sessions, /api/v1/profiles, etc.)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Authoritative Service Layer               |
|            (SessionService, MeasurementService)             |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Scientific Pipeline Engine                |
| (Image I/O, Card Detect, Perspective Warp, Optical Quality, |
|  CIE L*a*b* Calibration, ROI Extraction, Robust Estimation) |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     Domain State Machine                    |
|      (10 Master States, Transition Validation, Invariants)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      Repository Layer                       |
|   (SessionRepository, MeasurementRepository, AuditRepository)|
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     SQLite Data Store                       |
|              (SQLAlchemy ORM + Alembic Migrations)          |
+-------------------------------------------------------------+
```

---

## 3. Scientific Pipeline Flow

```
[RAW IMAGE BUFFER]
        ↓ (Format, Dimension, Channels & Provenance Validation)
[INGESTED IMAGE]
        ↓ (Canny Edges & Convex Quadrilateral Polygon Approximation)
[REFERENCE CARD LOCALIZATION]
        ↓ (4-Point Perspective Homography Warp: 600x400)
[CANONICAL CARD]
        ↓
    +---------------------------------------------------+
    | Optical Quality Gating (Adaptive Capture Guard)   |
    | - Blur: Laplacian variance >= 120.0               |
    | - Exposure: Mean luminance in [40, 220]           |
    | - Glare: Max reaction ROI specular fraction < 5%  |
    | - Skew: Perspective angle <= 20.0°                |
    | - Timing: Kinetic window in [10s, 120s]           |
    +---------------------------------------------------+
        ↓ (All Hard Gates Passed)
[REFERENCE CARD CALIBRATION] (Affine correction & Delta E76 residual <= 18.0)
        ↓
[ROI EXTRACTION] (Spatial erosion margins to eliminate pouch border noise)
        ↓
[ROBUST COLOR ESTIMATION] (Glare pixel masking, median & trimmed mean CIE L*a*b*)
        ↓
[VALIDATED MEASUREMENT DOMAIN CONTRACT]
        ↓
(Ready for Future Phase 4 Presumptive Classifier)
```

---

## 4. Module Boundaries & Responsibilities

| Module | Core Responsibility | Restrictions |
|---|---|---|
| `api/v1/` | Versioned HTTP routing, request/response serialization, dependency injection. | Thin route layer; delegates all business logic to services. |
| `scientific/` | Pure OpenCV and NumPy algorithms for optical quality, calibration, and color extraction. | Deterministic, pure functions; zero database/UI dependencies. |
| `domain/` | State machine rules, transition tables, offline identifier generators. | Pure Python, zero framework/DB dependencies. |
| `services/` | Session orchestration, transition enforcement, atomic audit logging. | Does not contain presentation or UI state. |
| `repositories/` | Typed queries, persistence operations, joined relations. | Encapsulates all SQLAlchemy queries; no raw SQL leakage. |
| `db/models/` | SQLAlchemy declarative ORM models for all domain entities. | No business logic in ORM models. |
| `security/` | Cryptographic primitives (Ed25519, SHA-256 canonicalization). | Deterministic, device-bound security primitives. |
