# Plan: Migrate frontend stack to React/Vite

**Change ID**: 260915-vwf1-migrate-react-frontend
**Date**: 2026-09-15
**Intake**: [intake.md](intake.md)

## Requirements

### Architecture: Frontend Guidelines
- **R1**: The project MUST deprecate Streamlit and mandate the React/Vite/Tailwind stack for the frontend UI.
  - *Scenario*: GIVEN a developer reads the constitution and context files, WHEN they look for frontend stack constraints, THEN they see React/Vite/Tailwind as the mandated stack and Zustand for state management.
- **R2**: The execution protocol MUST mandate explicit error handling for the frontend.
  - *Scenario*: GIVEN the `4.4 InteractiveStudio.tsx` implementation plan, WHEN handling API errors, THEN the app MUST catch 500 errors with a red (`#EF4444`) `ErrorBanner.tsx` and 422 errors with inline red text.
- **R3**: The `SpatialVector` payload in the execution protocol MUST contain the complete 12+ variable schema.
  - *Scenario*: GIVEN the payload specification in `website publishing.md`, WHEN the variables are listed, THEN `room_volume_m3` (float) and `space_use_type` (string) MUST be included.
- **R4**: The styling tokens MUST formally bridge the project's visual identity.
  - *Scenario*: GIVEN the Tailwind configuration in `website publishing.md`, WHEN the theme is defined, THEN `background: '#0E1117'`, `foreground: '#FFFFFF'`, and `border: 'rgba(255, 255, 255, 0.2)'` MUST be explicitly mapped.

## Tasks

### Phase 1: Core Documentation
- [ ] T001 [P] Update `fab/project/constitution.md` to deprecate Streamlit, mandate React/Vite/Tailwind, and authorize Zustand. <!-- R1 -->
- [ ] T002 [P] Update `fab/project/context.md` to reflect the React/Vite frontend architecture. <!-- R1 -->

### Phase 2: Execution Protocol
- [ ] T003 Update `website publishing.md` to include explicit error handling UI components. <!-- R2 -->
- [ ] T004 Update `website publishing.md` to add `room_volume_m3` and `space_use_type` to `SpatialVector`. <!-- R3 -->
- [ ] T005 Update `website publishing.md` to define the Tailwind theme extensions. <!-- R4 -->

## Acceptance

### Functional Completeness
- [ ] A-001 R1: `fab/project/constitution.md` and `fab/project/context.md` no longer mandate Streamlit and instead mandate React/Vite/Tailwind and Zustand.
- [ ] A-002 R2: `website publishing.md` explicitly describes `ErrorBanner.tsx` and inline validation error text.
- [ ] A-003 R3: `website publishing.md` explicitly lists `room_volume_m3` and `space_use_type`.
- [ ] A-004 R4: `website publishing.md` explicitly contains the Tailwind theme extension with `#0E1117` and `#FFFFFF`.

### Code Quality
- [ ] A-005 Pattern consistency: The markdown style and tone in all modified files remain consistent with the existing documentation.
- [ ] A-006 No unnecessary duplication: Shared definitions are not duplicated across multiple sections.

## Assumptions

0 assumptions.
