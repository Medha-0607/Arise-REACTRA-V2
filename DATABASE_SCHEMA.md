# REACTRA V2 — Database Schema Specification
**Engine**: SQLite  
**ORM**: SQLAlchemy 2.0+  
**Migrations**: Alembic  
**Target File**: `data/local/reactra_v2.db`  
**Schema Status**: Phase 2 Authoritative Schema Active  

---

## 1. Design Principles

1. **Local Authoritative Store**: SQLite is the authoritative offline persistence layer for local field operations.
2. **Schema Versioning**: Every table migration is managed sequentially using Alembic.
3. **Immutability & Tamper-Evidence**: Audit logs and evidence records are append-only.
4. **No Raw SQL Leakage**: All database access is encapsulated inside repository modules.
5. **Offline-Stable Identifiers**: Primary keys are globally unique strings generated without central auto-increment dependencies (e.g. `SES-YYYYMMDD-HHMMSS-RAND`).

---

## 2. Phase 2 Authoritative Table Schemas

### 2.1 `test_sessions`
Tracks core test workflow state, timestamps, and sealing indicators.
- `session_id` (PK, VARCHAR 64, Indexed)
- `status` (VARCHAR 32, Default: `'DRAFT'`, Indexed)
- `created_at` (DATETIME, Default: UTC Now)
- `updated_at` (DATETIME, Default: UTC Now)
- `is_sealed` (BOOLEAN, Default: `False`)

### 2.2 `assay_profiles`
Maintains versioned scientific assay definitions and algorithm bindings.
- `profile_id` (PK, VARCHAR 64)
- `name` (VARCHAR 128, Not Null)
- `reagent_name` (VARCHAR 64, Not Null)
- `profile_version` (VARCHAR 32, Not Null)
- `algorithm_version` (VARCHAR 32, Not Null)
- `reference_card_version` (VARCHAR 32, Not Null)
- `color_space` (VARCHAR 32, Default: `'CIE_LAB'`)
- `reagent_lot_required` (BOOLEAN, Default: `True`)
- `is_active` (BOOLEAN, Default: `True`)
- `description` (TEXT, Nullable)
- `created_at` (DATETIME, Default: UTC Now)

### 2.3 `procedural_context`
Preserves operator identity, case bindings, profile versions, and location provenance.
- `context_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Unique, Not Null)
- `case_id` (VARCHAR 64, Not Null, Indexed)
- `operator_id` (VARCHAR 64, Not Null, Indexed)
- `agency_id` (VARCHAR 128, Nullable)
- `profile_id` (FK -> `assay_profiles.profile_id`, Not Null)
- `profile_version_at_test` (VARCHAR 32, Not Null)
- `reference_card_id` (VARCHAR 64, Not Null)
- `capture_mode` (VARCHAR 32, Default: `'DIRECT_CAMERA'`)
- `location_provenance` (VARCHAR 256, Nullable)
- `reagent_lot_number` (VARCHAR 64, Nullable)
- `notes` (TEXT, Nullable)
- `created_at` (DATETIME, Default: UTC Now)

### 2.4 `reaction_timing`
Records incubation timeline and window compliance.
- `timing_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Unique, Not Null)
- `target_window_seconds` (INTEGER, Default: 30)
- `reaction_started_at` (DATETIME, Nullable)
- `capture_executed_at` (DATETIME, Nullable)
- `elapsed_seconds` (FLOAT, Nullable)
- `window_compliance_status` (VARCHAR 32, Default: `'PENDING'`)

### 2.5 `capture_records`
Holds capture metadata, image hashes, and pre-classifier quality status.
- `capture_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Unique, Not Null)
- `provenance_type` (VARCHAR 32, Default: `'DIRECT_CAMERA'`)
- `captured_at` (DATETIME, Default: UTC Now)
- `image_raw_uri` (VARCHAR 512, Nullable)
- `image_raw_sha256` (VARCHAR 64, Nullable)
- `quality_status` (VARCHAR 32, Default: `'PENDING'`)
- `failure_reason` (TEXT, Nullable)

### 2.6 `measurement_results`
Shell structure for raw extracted colorimetry and diagnostic telemetry (populated in Phase 3).
- `measurement_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Unique, Not Null)
- `status` (VARCHAR 32, Default: `'PENDING'`)
- `calculated_at` (DATETIME, Nullable)
- `algorithm_version` (VARCHAR 32, Nullable)
- `raw_color_space` (VARCHAR 32, Default: `'CIE_LAB'`)
- `metrics_json` (JSON, Nullable)
- `quality_diagnostics_json` (JSON, Nullable)

### 2.7 `evidence_records`
Shell structure for canonical snapshot, signature reference, and sealing state (populated in Phase 4).
- `evidence_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Unique, Not Null)
- `sealing_status` (VARCHAR 32, Default: `'UNSEALED'`)
- `canonical_json_sha256` (VARCHAR 64, Nullable)
- `envelope_signature` (TEXT, Nullable)
- `signature_algorithm` (VARCHAR 32, Default: `'Ed25519'`)
- `key_id` (VARCHAR 64, Nullable)
- `sealed_at` (DATETIME, Nullable)

### 2.8 `audit_events`
Append-only log of every state transition, user action, and system event.
- `event_id` (PK, VARCHAR 64)
- `session_id` (FK -> `test_sessions.session_id`, Not Null, Indexed)
- `event_type` (VARCHAR 64, Not Null)
- `from_state` (VARCHAR 32, Nullable)
- `to_state` (VARCHAR 32, Nullable)
- `timestamp` (DATETIME, Default: UTC Now, Indexed)
- `actor_id` (VARCHAR 64, Nullable)
- `device_id` (VARCHAR 64, Nullable)
- `payload` (JSON, Nullable)

### 2.9 `device_enrollments`
Enrolled local device hardware registration and status.
- `device_id` (PK, VARCHAR 64)
- `device_name` (VARCHAR 128, Not Null)
- `public_key_pem` (TEXT, Not Null)
- `enrolled_at` (DATETIME, Default: UTC Now)
- `is_active` (BOOLEAN, Default: `True`)

### 2.10 `trusted_key_registry`
Local store of trusted verification keys and authority credentials.
- `key_id` (PK, VARCHAR 64)
- `authority_name` (VARCHAR 128, Not Null)
- `public_key_pem` (TEXT, Not Null)
- `valid_from` (DATETIME, Default: UTC Now)
- `valid_until` (DATETIME, Nullable)
- `is_revoked` (BOOLEAN, Default: `False`)

---

## 3. Migration History
1. `cb628149b660_initial_foundation.py`: Base declarative model bootstrap.
2. `cb280e8353a3_phase2_authoritative_schema.py`: All 10 authoritative domain entities and indexes.
