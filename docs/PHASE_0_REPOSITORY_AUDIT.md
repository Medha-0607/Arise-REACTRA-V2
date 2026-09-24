# PHASE 0 REPOSITORY AUDIT: REACTRA V2
**Product**: REACTRA — Reaction-Aware Field Testing & Verifiable Evidence  
**Problem Statement**: SIH26231  
**Phase**: Phase 0 — Foundation & Architecture  
**Date**: September 2026  

---

## 1. Executive Summary

This document records the initial state audit of the REACTRA workspace (`REACTRA 1`), identifying authoritative sources, legacy artifacts, structural boundaries, and technical risks prior to scaffolding the V2 production foundation.

The primary objective of Phase 0 is to establish an extensible, clean, and strictly partitioned engineering foundation adhering to the non-negotiable product principles of presumptive field testing, offline-first reliability, tamper-evident record keeping, and strict architectural separation of concerns.

---

## 2. Inventory of Existing Workspace & Authoritative Sources

### 2.1 Workspace Initial State
- **Workspace Path**: `C:\Users\deena\REACTRA 1`
- **Initial File Count**: 0 files (Clean workspace).
- **Git State**: Initialized a dedicated repository isolated to `REACTRA 1`.

### 2.2 Authoritative Reference Documents
The following authoritative documents govern the product specifications and architectural decisions:
1. **`docs/REACTRA_PRD_V2.md`** (88.3 KB): Authoritative Product Requirements Document defining:
   - Presumptive colorimetric scope & non-definitive classification principles.
   - Dual-mode card workflows (Standard multi-well cards and legacy single-vial pouches).
   - Strict rejection thresholds for invalid measurements (blur, specular glare, underexposure, card misalignment).
   - Tamper-evident evidence chain (Ed25519 signing, SHA-256 canonicalization, cryptographic envelopes).
   - Offline-first operational mandate and privacy-preserving metadata handling.
2. **`docs/REACTRA_Master_Build_Spec_V2.md`** (71.1 KB): Master technical specification detailing:
   - Vision and perspective normalization pipeline parameters.
   - Colorimetric extraction, reference-card normalization, and distance metrics.
   - Domain state machine transitions and session lifecycles.
   - Cryptographic record canonicalization schemas.

---

## 3. Reusability, Architectural Alignment & Conflict Analysis

| Component / Artifact | Current Status | Architectural Alignment | Action / Migration Plan |
|---|---|---|---|
| **Authoritative PRD & Spec** | Staged in `docs/` | Fully aligned with V2 requirements. | Preserve in `docs/` as single source of product truth. |
| **Legacy Prototypes (V1 / Submission)** | External (`../REACTRA`) | Legacy code mixed business logic, heuristics, and ad-hoc scripts. | Do not copy directly. Specific algorithms (color conversion matrices, ROI geometry) will be cleanly adapted during Phase 2/3. |
| **Assay Profiles & Reference Cards** | Defined in PRD | Standardized JSON schema required for versioned assays (e.g., Marquis, Scott, Duquenois-Levine). | Scaffold `profiles/` directory and formalize schema in Phase 1. |

---

## 4. Key Architectural Safeguards & Separation of Concerns

To prevent architectural regression, the following strict separation rules are enforced:
1. **Presentation Layer (React + Vite + TypeScript)**:
   - Restricted strictly to user interaction, visual workflow, and state presentation.
   - **Prohibited**: Direct SQL access, OpenCV/WASM image processing, cryptographic signing, statutory legal heuristics.
2. **API Layer (FastAPI v1)**:
   - Versioned strictly under `/api/v1/`.
   - Lightweight request validation, dependency injection, and HTTP serialization only.
3. **Domain & Services Layer**:
   - Encapsulates session lifecycles, vision pipelines, explainable classification, and tamper-evident evidence generation.
4. **Data Layer (SQLAlchemy + Alembic + SQLite)**:
   - SQLite is authoritative for local offline-first storage.
   - All persistence is mediated through typed repository classes.

---

## 5. Technical Risks & Mitigation Strategies

| Risk | Severity | Description | Mitigation |
|---|---|---|---|
| **Illumination Variance & Glare** | High | Uncontrolled field lighting can distort colorimetric hue and chroma. | Strict pre-classifier validation filters (HSV / LAB color constancy, glare detection, reject-on-failure). |
| **False Sense of Finality** | Critical | Users or legal actors misinterpreting presumptive classification as forensic proof. | Explicit UI disclaimers, clear terminology (*"Presumptive Match Only"*), watermarked evidence PDFs. |
| **Offline Key & Chain Integrity** | High | Evidence tampering or clock drift on offline field devices. | Ed25519 device-bound keys, SHA-256 hash chaining, signed monotonic sequence counters. |
| **Script Execution Policies on Windows** | Low | PowerShell script execution restrictions (`npm.ps1`). | Use `cmd /c npm` or standard cross-platform npm CLI wrappers. |

---

## 6. Phase 0 Readiness Declaration

The workspace is ready for Phase 0 scaffolding:
- Directory tree initialized.
- Documentation and audit complete.
- Ready for backend (FastAPI + SQLAlchemy + Alembic), frontend (React + Vite + Tailwind + Zustand), and automated testing foundations.
