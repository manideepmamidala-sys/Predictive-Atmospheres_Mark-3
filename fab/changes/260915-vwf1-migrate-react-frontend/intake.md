# Intake: Migrate frontend stack to React/Vite

**Change ID**: 260915-vwf1-migrate-react-frontend
**Date**: 2026-09-15

## Origin

User request via `/fab-discuss` exploratory session to pivot the project architecture to a modern React/Vite/Tailwind stack and integrate recommended fixes.

## Why

The execution plan in `website publishing.md` violated the established system architecture and core directives defined in `fab/project/constitution.md` and `fab/project/context.md` (which previously mandated a Streamlit frontend). The decision was made to formally adopt the React/Vite/Tailwind stack and deprecate Streamlit, ensuring architectural consistency and allowing the use of Zustand for state management as proposed.

## What Changes

### 1. Constitution (`fab/project/constitution.md`)

- **Deprecate Streamlit**: Remove the Streamlit requirement from § III and § IV.
- **Adopt React/Vite/Tailwind**: Mandate the React/Vite/Tailwind stack for the frontend UI.
- **State Management**: Authorize `Zustand` for client-side state persistence instead of `st.session_state`.

### 2. Context (`fab/project/context.md`)

- Update the architecture description for `frontend/` to reflect the new React/Vite/Tailwind and Zustand stack instead of the Streamlit dashboard.

### 3. Execution Protocol (`website publishing.md`)

- **Error Handling**: Introduce explicit requirements in `4.4 InteractiveStudio.tsx` for catching and styling `500` and `422` API errors in the React UI (must not fail silently, surface in UI warning containers).
- **Spatial Parameter**: Add the missing 12th spatial parameter (along with any categorical variables) to the `SpatialVector` payload in § 2.2 to match the constitution.
- **Styling Tokens**: Refine the Tailwind specification in § 3.1 to ensure it formally bridges the "Predictive Atmospheres visual identity" design tokens.

## Affected Memory

(none)

## Impact

- `fab/project/constitution.md` (modify)
- `fab/project/context.md` (modify)
- `website publishing.md` (modify)

## Open Questions

(none)

## Assumptions

| #   | Grade   | Decision                        | Rationale                                                                                               | Scores |
| --- | ------- | ------------------------------- | ------------------------------------------------------------------------------------------------------- | ------ |
| 1   | Certain | Adopt React/Vite/Tailwind stack | User explicitly selected Option B during `/fab-discuss` to move forward with the React stack migration. |        |
