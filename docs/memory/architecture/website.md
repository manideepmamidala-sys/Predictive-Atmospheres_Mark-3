---
type: memory
description: "Eight-route React research atlas, validated static catalogue, component-level evidence, accessible figures and fused-only live Design Studio."
---
# Website Architecture

**Domain**: architecture

## Overview

`frontend/src/` is a React, Vite and TypeScript research atlas. Its eight routes are `/` (Predictive Atmospheres), `/study`, `/rooms`, `/body`, `/prediction`, `/studio`, `/explore` and `/methods`. The landing page presents the architectural question, hypothesis, three experiments, contribution and researcher context before directing readers to findings. Legacy route redirects preserve older links. The [platform](/architecture/platform.md) produces its evidence.

The public entry point is https://predictive-atmospheres.vercel.app. Root `vercel.json` hosts the static site and same-origin `/v1/*` FastAPI service together. The site service checks static assets before rewriting direct page requests to `index.html`. Publication is manual; the [deployment record](../../reports/revision-2026-10/deployment.md) distinguishes verified hosted checks from local test evidence.

## Requirements

### Static research and live Studio

Research routes read schema-validated, hash-checked products from `artifacts/results/`. A joined bundle serves shared views; the larger anti-aliased Signals product loads only when needed. The 28-card analysis catalogue is staged with versioned paths, including honest unavailable status for P4. Research routes remain readable if the API is asleep or unavailable. Only Studio prediction and generation call `/v1`; they expose readiness and errors without fabricated output.

Studio presents the fitted **fused** valence/arousal prediction only. Visitors can start from a complete E3 studied-room preset or supply all required independent room fields, choose a signed emotional target, and request direct prediction. A separate 0–100 numerical Neuro-Score drives constrained generation. Candidate results show requested, achieved and absolute score difference, support and the nearest studied room. Locks, ranges and category limits stay visible. The current `baseline_only` model gives a constant fused point across room geometries; moving the emotional target can change the score. Generated geometry is labelled schematic, and studied-room imagery is labelled as a reference rather than as the generated outcome.

### Evidence and interaction

The Study, Rooms, Body, Prediction and Methods routes distinguish observed inputs, reviewed physiology, reports, constructed fusion and model output. Figures show method, units, available-record denominators and limits. Data Explorer filters trials, rooms and people and exposes six component-level automated/reviewed QC records, reasons and reviewer provenance; heart rate and RMSSD remain distinct. Methods publishes 22 approved numerical settings, ten existing fusion-weight sensitivity summaries, CP-B review provenance and eight pinned references. Experiment 1 comfort remains separate from affect axes, and Experiment 2/3 rating procedures and complete/partial fusion states remain visible.

Light, Dark and System themes share design tokens and persist preference. Routes support deep links, keyboard access, responsive desktop/mobile layouts, reduced motion and chart alternatives. Room previews are WebP derivatives of retained Lumion renders; extraction of a top eye from stacked stereo imagery is an inferred presentation convention. The researcher portrait and approved contact/project links appear on the landing page. The landing page and footer display `manideepmamidala2@gmail.com` in working `mailto:` links; personal booklet, CV and portfolio files are not offered as downloads.

## Design Decisions

### Static research products with a narrow live API

**Decision**: Serve research routes from validated generated JSON and use the API for Studio actions only.
**Why**: The evidence remains readable during API cold starts and service outages.
**Rejected**: Making archived research pages depend on live computation.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Dual-theme evidence display

**Decision**: Use shared tokens and Light, Dark and System preferences for routes, figures and controls.
**Why**: Scientific plots, tables and source distinctions need readable contrast across devices and user settings.
**Rejected**: A single dark presentation for the complete research atlas.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Concept-led route structure

**Decision**: Lead with the research question and place component evidence, model findings, Studio, Explorer and Methods on distinct linked routes.
**Why**: Readers can understand the study's purpose before inspecting results, while detailed evidence remains accessible.
**Rejected**: Opening with numerical findings or merging all methods and interactions into the landing page.
*Introduced by*: 261010-tadj-research-atlas-design-studio

### Fused-only experimental Studio

**Decision**: Keep physiology and self-report comparisons on research routes and expose only the fitted fused model in Studio.
**Why**: The deployable artifact has one declared target and a weak baseline-only status; offering other prediction modes would imply unfit models exist.
**Rejected**: Fabricating separate objective or self-report live predictors.
*Introduced by*: 261010-tadj-research-atlas-design-studio
