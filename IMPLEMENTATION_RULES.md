# REACTRA V2 — Implementation & Code Quality Rules

---

## 1. Core Architectural Laws

1. **Separation of Concerns**:
   - `frontend/` contains only presentation, routing, and user interface state.
   - `backend/app/api/` contains only route handlers and schema validation.
   - `backend/app/services/` and `domain/` contain business logic.
   - `backend/app/database/` contains models and repository persistence logic.
2. **Offline-First Principle**:
   - The application must operate 100% locally without requiring internet access or cloud microservices.
3. **No Fake Functionality**:
   - Do not create stub methods that return mock "99.8% accurate positive" strings.
   - Scaffolded interfaces must explicitly raise `NotImplementedError` or return clean uninitialized states until their respective phase is implemented.
4. **Presumptive Integrity**:
   - All classifications are presumptive.
   - Invalid measurements must never reach the classifier.
   - Imported images must be flagged with `source: IMPORTED_IMAGE`.

---

## 2. Coding Standards

- **Python**: PEP 8 compliance, type annotations on all functions, Pydantic models for request/response payloads, docstrings on domain services.
- **TypeScript**: Strict mode enabled, explicit interfaces/types, no implicit `any`.
- **Error Handling**: Custom domain exception classes mapped to standardized HTTP status codes in FastAPI.
- **Testing**: Every new domain module must include unit tests verifying boundary conditions and deterministic outputs.
