# REACTRA V2

## Reaction-Aware Field Testing & Verifiable Evidence

**Smart India Hackathon (SIH) 2026** — **Problem Statement SIH26231**  
**Team:** ARISE

---

## 1. Problem

Presumptive colorimetric chemical testing in the field faces severe operational and evidentiary challenges:
* **Ambiguous Visual Interpretation:** Officers must judge subjective color changes under uncontrolled field illumination, glare, and shadows.
* **Lack of Measurement Validation:** A camera frame may suffer from motion blur, clipped exposure, or optical distortion, yet traditional tools attempt to classify defective images.
* **No Explainability or Audit Trail:** Field tests rarely preserve the mathematical rationale or decision margins behind a presumptive indication.
* **Evidentiary Vulnerability:** Test results, timestamps, custody transfers, and procedural metadata are susceptible to tampering or evidentiary dispute during judicial scrutiny.

> **Important:** Field testing is strictly presumptive. A field workflow must determine whether a captured measurement is valid, explain how the result was obtained, preserve the evidence cryptographically, and support later verification and laboratory referral—without claiming definitive laboratory confirmation.

---

## 2. Our Solution

**REACTRA V2** is an offline-first field evidence companion for presumptive colorimetric testing engineered around one core principle:

$$\textbf{MEASURE} \longrightarrow \textbf{EXPLAIN} \longrightarrow \textbf{PRESERVE}$$

REACTRA provides:
1. **Field Evidence Acquisition:** High-resolution optical capture with strict provenance labeling (`LIVE_CAMERA` vs `IMPORTED_IMAGE`).
2. **Deterministic Quality Gating (Adaptive Capture Guard):** Evaluates 6 physical parameters (card localization, blur, exposure, glare, perspective skew, color calibration) *before* classification.
3. **Profile-Driven Colorimetric Measurement:** Normalizes card perspective and extracts reaction-well CIE $L^*a^*b^*$ coordinates calibrated against a 6-patch color standard.
4. **Controlled Four-State Presumptive Classification:** Evaluates Euclidean distance ($\Delta E$) against specification-bound assay profiles.
5. **Cryptographic Evidence Sealing:** Canonicalizes record metadata (RFC 8785), computes SHA-256 digests, and generates Ed25519 digital signatures.
6. **Verification & Tamper Detection:** Standalone mathematical verification of digital signatures, digest matches, and monotonic hash chains.
7. **Custody & Laboratory Referral:** Generates formal referral packages with tamper-evident QR codes and chain-of-custody logging.
8. **100% Offline Capability:** All core measurement, classification, evidence sealing, and verification algorithms operate locally without external network dependencies.

---

## 3. Four Presumptive Outcome States

REACTRA enforces four mutually exclusive presumptive outcome states:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 CAPTURE & QUALITY GATE                 │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       │ Quality Passed?                             │
                      YES                                            NO
                       │                                             │
          ┌────────────┴────────────┐                     ┌──────────┴──────────┐
          │   CALIBRATED SAMPLING   │                     │   INVALID CAPTURE   │
          └────────────┬────────────┘                     └─────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
   ΔE ≤ Threshold  ΔE ≥ Threshold In-Between
         │             │             │
         ▼             ▼             ▼
   ┌───────────┐ ┌───────────┐ ┌───────────┐
   │PRESUMPTIVE│ │PRESUMPTIVE│ │INCONCLUSIVE│
   │ POSITIVE  │ │ NEGATIVE  │ │           │
   └───────────┘ └───────────┘ └───────────┘
```

1. **`PRESUMPTIVE_POSITIVE`:** Reaction color matches the target analyte profile within the positive decision boundary ($\Delta E \le \text{Threshold}_{\text{pos}}$).
2. **`PRESUMPTIVE_NEGATIVE`:** Reaction color does not match the target analyte and falls within the negative baseline boundary ($\Delta E \ge \text{Threshold}_{\text{neg}}$).
3. **`INCONCLUSIVE`:** Reaction color falls within the cautionary transition margin between thresholds; mandatory supervisor review required.
4. **`INVALID_CAPTURE`:** Optical quality, card localization, illumination, or incubation timing failed pre-classification quality gates.

> **Invariants:**  
> • Invalid captures are strictly prohibited from reaching the classifier.  
> • Unknown or mismatched assay profiles cannot be classified.

---

## 4. Key Features

### Offline-First Operation
Core measurement, color calibration, classification, evidence sealing, custody logging, and verification operate completely offline on local device storage.

### Adaptive Capture Guard (Pre-Classifier Quality Gate)
Automated multi-parameter optical verification:
* **Reference Card Localization:** Contour quadrilateral detection ($1.50 \pm 0.45$ aspect ratio verification).
* **Motion & Focus Blur Check:** Laplacian variance threshold ($\text{Variance} \ge 120.0$).
* **Exposure & Dynamic Range:** Histogram distribution analysis to reject clipped/underexposed frames.
* **Specular Glare Gating:** Reagent well highlight ratio filter ($\text{Glare} \le 5.0\%$).
* **Keystone & Perspective Alignment:** Perspective rectification with skew angle limit ($\text{Skew} \le 20.0^\circ$).
* **Colorimetric Calibration:** Affine least-squares illumination correction across 6 reference patches ($\text{Residual} \le 18.0\text{ ΔE}$).
* **Reaction Kinetics Window:** Enforces mandatory incubation timing windows ($t_{\text{min}} \le t \le t_{\text{max}}$).

### Profile-Driven Scientific Architecture
All measurement parameters, target CIE $L^*a^*b^*$ centroids, decision thresholds, and kinetic timing windows are strictly bound to versioned assay profiles (e.g., `MARQUIS-STANDARD-V1`).

### Cryptographic Evidence Integrity
* **Canonical Serialization:** Deterministic RFC 8785 canonical JSON formatting.
* **Cryptographic Hashing:** SHA-256 content digests covering all measurement, procedural, and sensor metadata.
* **Digital Signatures:** Asymmetric Ed25519 digital signatures generated with device-enrolled private keys.
* **Monotonic Hash Chain:** Chronological tamper-evident chaining (`previous_record_hash`).

### Verification & Tamper Detection
Independent verification endpoint recalculates canonical digests and validates public key cryptography, immediately detecting bit-level tampering or sequence manipulation.

### Procedural Context & Custody Logging
Records statutory field metadata (Section 50/52A/57 NDPS Act compliance flags, witness panchnama references, kit lot numbers) and maintains an append-only chain-of-custody transfer log.

---

## 5. Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND PRESENTATION LAYER                       │
│             React 18 + TypeScript + Vite + TailwindCSS + Zustand        │
│        (StepIndicator, CaptureViewport, QualityCard, EvidenceSeal)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST API (v1)
┌───────────────────────────────────▼────────────────────────────────────┐
│                         FASTAPI BACKEND SERVICE                        │
│                Routers: /sessions, /measure, /classify, /seal          │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
┌───────────────────▼──────────────┐   ┌─────────────▼───────────────────┐
│    SCIENTIFIC MEASUREMENT CORE   │   │     EVIDENCE INTEGRITY ENGINE   │
│  • Image Ingest & Provenance     │   │  • RFC 8785 Canonicalization    │
│  • Card Detection & Homography   │   │  • SHA-256 Digest Computation   │
│  • Glare & Blur Quality Gates    │   │  • Ed25519 Signature Generation │
│  • Affine Color Calibration      │   │  • Monotonic Hash Chaining      │
│  • Robust ROI K-Means Extraction │   │  • QR Referral Exporter         │
└───────────────────┬──────────────┘   └─────────────┬───────────────────┘
                    │                                │
┌───────────────────▼────────────────────────────────▼───────────────────┐
│                    PERSISTENCE & STATE MACHINE LAYER                   │
│       SQLite Local Database + SQLAlchemy ORM + Domain State Machine    │
│        (Sessions, Measurements, ProceduralContext, AuditEvents)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Technology Stack

### Backend
* **Python 3.11**
* **FastAPI:** High-performance asynchronous REST API framework
* **SQLAlchemy & SQLite:** Robust relational persistence and offline transactions
* **Pydantic V2:** Strict schema validation and typed domain models
* **OpenCV (`cv2`):** Computer vision, edge detection, contour approximation, and perspective transformation
* **NumPy:** Colorimetric coordinate transformation and matrix operations
* **Pillow (`PIL`):** High-resolution image generation and PDF compilation
* **Cryptography:** Asymmetric Ed25519 digital signatures and SHA-256 digests

### Frontend
* **React 18**
* **TypeScript**
* **Vite:** Next-generation frontend tooling and production bundler
* **TailwindCSS:** Custom tactical dark-mode design system
* **Zustand:** Deterministic workflow and session state management
* **Lucide React:** Tactical interface iconography
* **HTML5 MediaDevices / WebRTC:** Real camera acquisition with environment sensor fallback

---

## 7. Project Structure

```
Arise-REACTRA-V2/
├── backend/
│   ├── app/
│   │   ├── api/v1/             # REST API routes (sessions, profiles, health)
│   │   ├── domain/             # State machine, identifiers, domain enums
│   │   ├── db/                 # Database models, connection sessions
│   │   ├── repositories/       # Data access repositories
│   │   ├── schemas/            # Pydantic V2 request & response schemas
│   │   ├── scientific/         # Scientific pipeline (card detection, blur, glare,
│   │   │                       # calibration, ROI, robust estimation, classifier)
│   │   ├── security/           # Cryptography, canonicalization, Ed25519, hashing
│   │   ├── services/           # Application orchestration services
│   │   ├── config.py           # Typed environment configuration
│   │   └── main.py             # FastAPI application entrypoint
│   └── tests/                  # 84 automated pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # 10 Golden Journey workflow pages
│   │   ├── services/           # REST API client
│   │   ├── stores/             # Zustand store (useWorkflowStore)
│   │   ├── types/              # TypeScript domain types
│   │   └── main.tsx            # React application root
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── reference_cards/            # Authoritative 150x100mm optical test fixture assets
│   ├── REACTRA_DEMO_REFERENCE_CARD_HIGHRES.png
│   ├── REACTRA_DEMO_REFERENCE_CARD.pdf
│   ├── REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.png
│   ├── REACTRA_DEMO_REFERENCE_CARD_A4_PRINT_SHEET.pdf
│   └── README.md
├── scripts/                    # Asset generator and validation scripts
│   └── generate_physical_reference_card.py
├── docs/                       # Technical specs, PRD, architecture, and audit logs
├── .env.example                # Environment configuration template
├── .gitignore                  # Comprehensive secret & build exclusion rules
└── README.md                   # System documentation
```

---

## 8. Running Locally

### Prerequisites
* **Python 3.11+**
* **Node.js 18+ & npm**
* **Git**

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server will start at `http://127.0.0.1:8000` (Interactive Swagger docs: `http://127.0.0.1:8000/docs`).

### Frontend Setup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite development server
npm run dev
```

The web application will open at `http://localhost:5173`.

---

## 9. Testing & Quality Verification

All components are covered by automated unit, integration, and property-based tests.

### Run Backend Test Suite

```bash
# From workspace root or backend directory
python -m pytest backend/tests -v
```

**Current Verified Baseline:**
* **84 passed in 7.32s** (100% pass rate across state machine, scientific pipeline, classifier, cryptography, hash chain, custody, and API endpoints).

### Run Frontend Production Build

```bash
cd frontend
npm run build
```

**Current Verified Baseline:**
* **Clean TypeScript compilation and Vite production build** (0 errors, 0 warnings).

---

## 10. Scientific & Operational Boundary

> **MANDATORY NOTICE: PRESUMPTIVE TESTING ONLY**  
> REACTRA is a field evidence companion engineered for presumptive colorimetric screening and verifiable evidence preservation.  
> • It does **NOT** perform or claim confirmatory chemical analysis.  
> • All field results are presumptive and must be confirmed by accredited forensic laboratory testing (GC-MS, LC-MS, FTIR).  
> • The physical reference-card fixture in this repository is an optical calibration aid and software test standard—it is **NOT** a real chemical test.  
> • Scientific thresholds and profile parameters are specification-derived engineering parameters and require empirical physical validation before operational deployment.

---

## 11. Cryptographic Boundary

> **MVP Cryptographic Specification:**  
> • The current MVP implementation employs software-backed Ed25519 digital signatures and local SQLite persistence for demonstration and evaluation.  
> • Hardware-backed key isolation (TPM 2.0 / Android Keystore / Apple Secure Enclave) and centralized public key infrastructure (PKI) enrollment represent future production hardening.

---

## 12. SIH Golden Demo Journey

For judges and evaluators, the complete end-to-end field journey follows 10 integrated steps:

$$\begin{aligned}
\textbf{SETUP} &\longrightarrow \textbf{CAPTURE} \longrightarrow \textbf{QUALITY CHECK} \longrightarrow \textbf{ANALYSIS} \longrightarrow \textbf{RESULT} \\
&\longrightarrow \textbf{EVIDENCE PASSPORT} \longrightarrow \textbf{QR / REFERRAL} \longrightarrow \textbf{VERIFY} \longrightarrow \textbf{CUSTODY} \longrightarrow \textbf{TIMELINE}
\end{aligned}$$

1. **Setup (`/setup`):** Configure operator badge, case event ID, and select assay profile (`MARQUIS-STANDARD-V1`).
2. **Capture (`/capture`):** Acquire specimen frame via real camera stream or reference card upload (`IMPORTED_IMAGE`).
3. **Quality Check (`/check`):** Adaptive Capture Guard evaluates blur, exposure, glare, localization, perspective, and color calibration.
4. **Analysis (`/analysis`):** Perspective normalization, ROI extraction, and K-Means clustering.
5. **Result (`/result`):** Four-state presumptive classification with explainable $\Delta E$ distance and decision margin breakdown.
6. **Evidence Passport (`/evidence`):** Cryptographic sealing with SHA-256 digest and Ed25519 signature.
7. **Referral Package (`/referral`):** Printable referral document and tamper-evident QR code.
8. **Verification (`/verify`):** Independent cryptographic validation proving record integrity and detecting tampering.
9. **Custody (`/custody`):** Physical evidence transfer logging with recipient officer details.
10. **Timeline (`/timeline`):** Complete immutable chronological audit trail.

---

## 13. Team

* **Team Name:** ARISE
* **Competition:** Smart India Hackathon (SIH) 2026
* **Problem Statement:** SIH26231
