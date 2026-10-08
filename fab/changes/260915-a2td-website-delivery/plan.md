# Plan: Predictive Atmospheres Thesis Website
[Intake](intake.md) • [Plan](plan.md)

## Requirements

### Website: Structure & Routing
- **R1**: The application SHALL use `react-router-dom` to support three distinct routes (`/`, `/research`, and `/platform`).
  - GIVEN a user navigates to `/`, THEN they should see the Landing Page.
  - GIVEN a user navigates to `/research`, THEN they should see the Research narrative.
  - GIVEN a user navigates to `/platform`, THEN they should see the interactive React dashboard.
- **R2**: The application SHALL include a persistent global `NavBar` component for cross-route navigation.

### Website: Aesthetics & Theme
- **R3**: The application SHALL implement a deep dark mode theme as the default and only theme, utilizing high-contrast white text and neon accents (electric blue/cyber-green) inspired by Strelka New Normal / MIT Media Lab.
- **R4**: The application SHALL utilize brutalist typography (Inter/Space Grotesk) and structural layouts with generous negative space.
- **R5**: The application SHALL use `framer-motion` to provide fluid page transitions and scroll-triggered animations.

### Website: Landing Page (`/`)
- **R6**: The Landing Page SHALL feature a full-screen looping background video using `PredictiveAtmospheres_Project Video.mp4`.
- **R7**: The Landing Page SHALL present a bold title and primary Call-To-Action (CTA) buttons linking to `/research` and `/platform`.

### Website: Research Page (`/research`)
- **R8**: The Research Page SHALL present a scroll-driven narrative timeline explaining Mark 1 through Mark 3.
- **R9**: The Research Page SHALL integrate the high-resolution InDesign exports from `frontend/public/assets/images` to visually support the narrative.

### Website: Platform Page (`/platform`)
- **R10**: The Platform Page SHALL embed the existing `InteractiveStudio` machine learning dashboard components without breaking their current interactive functionality.

## Tasks

### Phase 1: Setup
- [ ] T001 [P] `frontend/package.json`: Ensure `framer-motion` is installed as a dependency. <!-- R5 -->
- [ ] T002 [P] `frontend/src/index.css`: Update the global CSS tokens to enforce the deep dark mode, brutalist typography, and neon accents. <!-- R3 --> <!-- R4 -->

### Phase 2: Core Implementation
- [ ] T003 `frontend/src/App.tsx`: Refactor the application root to use a `Routes` layout enclosing the `/`, `/research`, and `/platform` paths, wrapped inside a `BrowserRouter` (or handled via `main.tsx`). <!-- R1 -->
- [ ] T004 `frontend/src/components/NavBar.tsx`: Implement the global persistent navigation bar with brutalist styling and links to the three routes. <!-- R2 -->
- [ ] T005 `frontend/src/pages/PlatformPage.tsx`: Move the existing dashboard layout (currently in `App.tsx`) into this dedicated component. <!-- R10 -->

### Phase 3: Integration & Edge Cases
- [ ] T006 `frontend/src/pages/LandingPage.tsx`: Implement the hero section with the looping `<video>` tag pointing to the `PredictiveAtmospheres_Project Video.mp4` asset, overlaid with title and framer-motion powered CTAs. <!-- R6 --> <!-- R7 -->
- [ ] T007 `frontend/src/pages/ResearchPage.tsx`: Implement the scroll-driven narrative utilizing `framer-motion` `useScroll` or `whileInView`, mapping through the images in `frontend/public/assets/images`. <!-- R8 --> <!-- R9 -->

### Phase 4: Polish
- [ ] T008 `frontend/src/pages/*`: Apply consistent page transition animations to all top-level routes using `framer-motion` `AnimatePresence`. <!-- R5 -->

## Acceptance

### Functional Completeness
- [x] A-001 R1: Navigating to `/`, `/research`, and `/platform` correctly renders the respective pages without full page reloads.
- [x] A-002 R2: The NavBar is visible on all pages and its links function correctly.
- [x] A-003 R3: The application renders in dark mode with white text and neon accents.
- [x] A-004 R4: Brutalist typography and generous padding/margins are visible across all layout components.
- [x] A-005 R5: `framer-motion` transitions play smoothly on initial page load and route changes.
- [x] A-006 R6: The background video on the Landing Page loops seamlessly and autoplays.
- [x] A-007 R7: Landing page CTAs successfully route the user to `/research` and `/platform`.
- [x] A-008 R8: The Research Page provides a continuous scrolling narrative experience.
- [x] A-009 R9: The InDesign export images render successfully within the Research Page.
- [x] A-010 R10: The ML dashboard (InteractiveStudio) on the Platform Page functions as it did previously.

### Code Quality
- [x] A-011: Follows existing pattern consistency for React functional components and hooks.
- [x] A-012: No unnecessary duplication of layout containers; shared components (like typography headers) are reused.

## Notes

## Deletion Candidates

- `frontend/src/components/HeroSection.tsx` — Replaced by the new `LandingPage.tsx` route.
- `frontend/src/components/ResearchNarrative.tsx` — Replaced by the new scroll-driven `ResearchPage.tsx`.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Confident | Use `framer-motion` for animations | Standard React animation library, highly capable of scroll-driven narratives. | S:80 R:80 A:90 D:90 |
| 2 | Certain | Move existing App.tsx logic to PlatformPage.tsx | The previous design was a monolithic App.tsx; this needs to be decoupled to allow the new routes to exist. | S:90 R:90 A:100 D:90 |
| 3 | Confident | Serve the video from `public/assets` | Vite natively supports serving large media files from the public directory. | S:80 R:80 A:90 D:90 |
