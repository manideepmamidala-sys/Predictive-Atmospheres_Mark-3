---
type: memory
description: "Architecture and routing definitions for the Predictive Atmospheres thesis website, detailing the MPA-style navigation, framer-motion transitions, and brutalist design theme."
---

# Website Architecture

## Overview
The Predictive Atmospheres frontend is a React/Vite application designed for the final thesis delivery. It utilizes a Multi-Page Application (MPA) style navigation structure powered by `react-router-dom` to separate the experiential narrative from the functional Machine Learning dashboard. 

## Requirements
- The application must support distinct routes for different experiences (Landing, Research, Platform).
- Transitions between pages must be smooth and cinematic, utilizing `framer-motion`.
- The aesthetic must follow a brutalist design system (Strelka / MIT Media Lab inspired), featuring deep dark mode, neon accents, and `Space Grotesk` / `Inter` typography.
- The Interactive ML dashboard must be preserved without altering its core functionality.

## Design Decisions

### Client-Side Routing via React Router
**Why:** To provide distinct URLs for different parts of the thesis presentation without sacrificing the fluid, state-preserving nature of a React application.
**Rejected:** Next.js (too heavyweight for a client-side ML app), native `<a>` tags (causes full page reloads and breaks ML state).
*Introduced by*: 260915-a2td-website-delivery

### Framer Motion for Page Transitions
**Why:** To provide an immersive, cinematic experience fitting for a thesis presentation. `AnimatePresence` seamlessly handles exit and enter animations during route changes.
**Rejected:** CSS keyframes (hard to orchestrate component unmounting), React Spring (steeper learning curve for simple opacity fades).
*Introduced by*: 260915-a2td-website-delivery

### Scroll-Driven Narrative for Research Page
**Why:** To present high-resolution InDesign exports chronologically without overwhelming the user or browser memory.
**Rejected:** A standard PDF viewer embed (clunky UX), a carousel (hides information and breaks reading flow).
*Introduced by*: 260915-a2td-website-delivery

### Component Cleanup (Future)
The `HeroSection.tsx` and `ResearchNarrative.tsx` components were made obsolete by the new routing structure and are candidates for deletion.
