# Intake: Predictive Atmospheres Thesis Website
[Intake](fab/changes/260915-a2td-website-delivery/intake.md) • 2026-09-15

## Origin
Generated via `/fab-new website-delivery` after aligning with the user in a `/fab-discuss` session. The goal is to create the final online delivery for the thesis submission.

## Why
The user needs a published, Vercel-hosted online website that acts as the final thesis submission. This website must host both the interactive React/Vite ML dashboard (developed in a previous step) and a clear research narrative section explaining what the project is, key milestones, and featuring a teaser video. The aesthetic must be clean, polished, and inspired by Strelka New Normal or MIT Media Lab.

## What Changes

### 1. Website Routing and Structure
- Implement `react-router-dom` to support a Multi-Page Application feel over the existing Single Page App structure.
- Add three distinct routes:
  - `/`: Landing/Hero page.
  - `/research`: The narrative storytelling page.
  - `/platform`: The interactive React dashboard.

### 2. Aesthetic Overhaul
- Implement a deep dark mode with stark white text and subtle neon accents (electric blue/cyber-green).
- Apply brutalist/minimalist layout principles with large typography (Inter, Space Grotesk, or Helvetica) and generous negative space.
- Use `framer-motion` for fluid scroll-triggered fade-ins and page transitions.

### 3. Landing Page (`/`)
- A full-screen entry featuring a looping teaser video (`frontend/public/assets/PredictiveAtmospheres_Project Video.mp4`).
- A bold title ("Predictive Atmospheres") and clear CTAs linking to `/research` and `/platform`.

### 4. Research Page (`/research`)
- A scroll-driven narrative that breaks down the neuro-architectural approach (Mark 1 through Mark 3).
- Weave the high-resolution InDesign exports (currently stored in `frontend/public/assets/images`) into the narrative timeline.

### 5. Platform Page (`/platform`)
- Embed the existing InteractiveStudio components seamlessly into the new routing structure without altering their core functionality.

## Affected Memory
- (none)

## Impact
- Extensive UI/UX updates and additions to the `frontend/` directory.
- No changes to the `src/` Python ML backend.
- The `frontend/` directory will be primed for Vercel deployment.

## Open Questions
- None. (All structural and asset-related questions were resolved during the `/fab-discuss` phase).

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|---|---|---|---|
| 1 | Certain | Use `react-router-dom` and `framer-motion` | Standard tools for modern React SPA routing and animations, aligning with the Vite/TS stack. | S:90 R:90 A:100 D:90 |
| 2 | Confident | Embed the existing `InteractiveStudio` at `/platform` | Confirmed with the user during the discussion phase. | S:80 R:80 A:90 D:80 |
| 3 | Confident | Use `PredictiveAtmospheres_Project Video.mp4` as the hero background | User explicitly supplied this MP4 for the teaser video requirement. | S:80 R:80 A:90 D:80 |
| 4 | Confident | Use images from `frontend/public/assets/images` for the narrative | User exported their InDesign booklet assets to this folder per the discussion. | S:80 R:80 A:90 D:80 |
