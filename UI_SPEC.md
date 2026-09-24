# REACTRA V2 — UI / Frontend Specification
**Framework**: React 18+  
**Language**: TypeScript  
**Build Tool**: Vite  
**Styling**: Tailwind CSS  
**Icons**: Lucide React  
**Routing**: React Router DOM  
**State**: Zustand  

---

## 1. UI Principles & Field Design Mandates

1. **High Contrast & Field-Legibility**: Designed for outdoor sunlight and dim squad car environments. Clean typography, high contrast borders, and prominent state indicators.
2. **Explicit Presumptive Language**: Every classification or test screen must prominently display:
   > *"PRESUMPTIVE FIELD TEST ONLY — NOT A CONFIRMATORY CHEMICAL ANALYSIS"*
3. **Deterministic State Progression**: Workflow guided step-by-step (Kit Selection -> Pre-Capture -> Validation -> Result -> Evidence Packaging).
4. **No UI-Side Heuristics**: The UI is purely a presentation layer. It does not compute color differences, apply thresholds, or sign records.

---

## 2. Phase 0 Frontend Foundation Shell

Phase 0 provides:
- App Shell with header, navigation bar, and main content area.
- Centralized `apiClient` configured with base URL from environment variables.
- React Router configuration with Home/Dashboard placeholder and System Status view.
- Global Error Boundary for crash resilience.
- Tailwind CSS setup with custom dark/slate tactical theme.
