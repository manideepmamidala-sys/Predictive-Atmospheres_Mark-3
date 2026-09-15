# Predictive Atmospheres Constitution

## Core Principles

### I. Architectural Separation of Concerns
The backend (`src/`) SHALL remain a pure Python ML backend with zero UI dependencies. The frontend (`frontend/ui/`) MUST never process raw data directly; it SHALL only read from processed `.parquet` / `.csv` files or query backend services.

### II. Spatial Input and Feature Integrity
The system MUST enforce strict schema validation via Pydantic on the 12 independent spatial variables (+ categoricals). Derived features SHALL only be computed by the backend feature engineering pipeline. Purged metrics (UDI, sDA, ASE) SHALL NOT be reintroduced.

### III. UI/UX and Theming Discipline
The frontend UI SHALL adhere strictly to project design manifests, typography tokens, and custom dark theme tokens. The frontend UI MUST use the React/Vite/Tailwind stack. Standard browser fonts and default Plotly colorways (Viridis, Plasma) SHALL NOT be used. Native framework components MUST be preferred over manual HTML/CSS pseudo-elements.

### IV. Resilient Error Handling and State Persistence
Backend processes MUST never fail silently; errors SHALL be caught and surfaced through styled UI warning containers. Heavy models, boundaries, and datasets SHALL be cached in `Zustand` (for client-side state) or service-level caches to prevent performance degradation across UI reruns.

### V. Multimodal Ground-Truth Governance
Emotion ground truth targets MUST be synthesized exclusively through the multimodal affective fusion protocol (combining objective FAA/ECG metrics with subjective scores parameterized by α in `FusionConfig`). Raw EEG/ECG signals SHALL be validated before ingestion.

## Additional Constraints

### Test Integrity
Tests MUST conform to the implementation spec — never the other way around. When tests fail, the fix SHALL either (a) update the tests to match the spec, or (b) update the implementation to match the spec. Modifying implementation code solely to accommodate test fixtures or test infrastructure is prohibited. Specs are the source of truth; tests verify conformance to specs.

## Governance

**Version**: 1.0.0 | **Ratified**: 2026-09-15 | **Last Amended**: 2026-09-15
