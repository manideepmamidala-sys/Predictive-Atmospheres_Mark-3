# Design Document — Neuro-Architecture Affective Prediction Platform (Dark Theme Redesign v1.0)

## 1. Introduction
This document defines a full visual and UX redesign for the Neuro-Architecture Affective Prediction Platform.
The new direction blends:
- Neon, spatial, topographic aesthetics (from Image 0), and
- Structured, enterprise analytics dashboard patterns (from Image 1).

Outcome: a professional, research-grade interface that feels futuristic but remains clear, data-dense, and decision-oriented.

## 2. Product Vision
- Transform biometric + spatial ML outputs into design decisions architects can act on.
- Keep scientific credibility while improving usability for long research sessions.
- Make inference, model comparison, and design iteration feel like one continuous workflow.

## 3. Design Goals
- **Professional Clarity:** clean hierarchy for complex EEG/ECG + ML data.
- **Aesthetic Sophistication:** dark UI with a purple-first visual system, high visual contrast, and low fatigue.
- **Actionable Analytics:** every chart ties to a design choice (geometry, target emotion, confidence).

## 4. Visual Identity

### 4.1 Color System (Semantic Tokens)
- **Base Background:** `#121212`
- **Surface 1 (cards/panels):** `#1A1A1A`
- **Surface 2 (elevated):** `#222228`
- **Text Primary:** `#E0E0E0`
- **Text Secondary:** `#A3A3B2`
- **Grid/Dividers:** `#2A2A36`
- **Accent Primary (Purple 500):** `#8A5CFF`
- **Accent Purple Deep (Purple 700):** `#5E35D6`
- **Accent Purple Soft (Purple 300):** `#B79CFF`
- **Complementary Accent (Yellow-Gold):** `#D4C94A`
- **Triadic Accent A (Teal):** `#2EC4B6`
- **Triadic Accent B (Orange):** `#FF9F1C`
- **Warning:** `#D4C94A`
- **Critical:** `#FF9F1C`
- **Success:** `#2EC4B6`

**Gradients**
- `linear(135deg, #5E35D6 -> #8A5CFF -> #B79CFF)` for primary charts and hero surfaces.
- `linear(135deg, #2EC4B6 -> #8A5CFF -> #FF9F1C)` only when three-way comparison or triadic emphasis is needed.
- `linear(180deg, #8A5CFF 20% -> transparent)` for subtle overlays.

**Color-Theory Usage Rules**
- Purple shades are the default for all interactive and data-focused UI states.
- If one non-purple accent is needed, use the complementary yellow-gold (`#D4C94A`).
- If two non-purple accents are needed, use the triadic pair teal (`#2EC4B6`) and orange (`#FF9F1C`).

**Glow Usage (strict)**
- Primary glow: 8-16px blur in purple shades for active data only.
- No glow on body text or non-interactive UI to preserve professionalism.

### 4.2 Typography
- Primary family: Inter (fallback: Roboto, SF Pro, sans-serif).
- Type scale:
  - H1: 28/36 semibold
  - H2: 20/28 semibold
  - H3: 16/24 medium
  - Body: 14/22 regular
  - Caption: 12/18 regular
- Numeric data: tabular numbers enabled for metric alignment.

### 4.3 Shape, Spacing, Elevation
- 12-column desktop grid, 24px gutters, 24px outer margins.
- Panel radius: 14px.
- Spacing scale: 4, 8, 12, 16, 24, 32.
- Elevation: soft shadow + 1px inner border (`#2A2A36`).

## 5. Information Architecture
Left vertical sidebar navigation:
1. Dashboard (Overview)
2. Data Ingestion
3. Signal Processing
4. Model Training & Results
5. Spatial Prediction

Global top bar:
- Project selector
- Active experiment/session
- Run status indicator
- User profile/settings

## 6. Dashboard Layout (Primary Screen)

### Segment 1: Input & Configuration
- **Panel 1: Experiment Metadata (Top Left)**
  - Upload/load split metadata files (`*_spatial data.csv` and `*_biometric data.csv`), EEG/ECG directories, and dataset preview.
  - Validation chips: schema status, missing files, subject count, and experiment readiness (`Planned`/`Ready`).
  - Auto-discovered optional parameter tags for newly added spatial/biometric columns.
- **Panel 2: Signal Processing Status (Top Middle)**
  - 3 circular gauges: baseline correction, normalization, feature extraction.
  - Ring style: neon-purple progress + muted track.
  - Includes elapsed time and queue state.

### Segment 2: Biometric Analysis
- **Panel 3: EEG Feature Landscape (Center Large)**
  - Interactive 3D neon wireframe.
  - Encodes feature intensity (e.g., alpha/beta power or latent embeddings).
  - Controls: rotate, pan, feature-band toggle, condition filter, snapshot.
- **Panel 4: Affective Mapping (Right)**
  - Default: Valence/Arousal circumplex with confidence ellipse.
  - Toggle: radar chart for feature importance (WWR, height, volume, etc.).
  - Live legend for contribution weights and uncertainty.

### Segment 3: Prediction & Design Integration
- **Panel 5: Model Predictions (Bottom Left)**
  - Grouped bars comparing scenarios (Room A/B/C).
  - Gradient bars use purple shades by default; complementary/triadic colors only for comparison overlays, with error bars for confidence.
- **Panel 6: Predictive Mapping View (Bottom Middle)**
  - Room wireframe + projected emotion heatmap.
  - Layer toggles: valence, arousal, category probability.
  - Click surface region to inspect local emotional score.
- **Panel 7: Activity/Results Feed (Bottom Right)**
  - Chronological list of runs, metrics, saved outputs.
  - Row format: event type, timestamp, status, quick action.

## 7. Component System
- Sidebar with icon+label, active neon rail.
- Metric cards with sparkline and delta.
- Circular progress gauges (single and stacked modes).
- 3D landscape viewer container.
- Circumplex + radar chart module.
- Scenario comparison chart block.
- Run/event feed list with status pills.
- Notification toasts (success/warning/error).

## 8. Interaction Design
- Hover: subtle border brighten + 2% surface lift.
- Active selection: accent outline + glow.
- Cross-filtering:
  - Selecting a scenario updates Panels 3, 4, 6, and feed context.
- Drill-down:
  - Click any metric to open right-side detail drawer.
- Keyboard:
  - Full tab flow and focus ring visibility.

## 9. Motion Guidelines
- Duration: 120–220ms standard; 280ms for chart transitions.
- Easing: ease-out for entrance, ease-in-out for updates.
- Motion is informative, not decorative (no ambient animations by default).

## 10. Accessibility
- Minimum contrast target: WCAG AA for text and controls.
- Color is never sole carrier of meaning (shape/label redundancy required).
- Screen-reader labels for all chart controls and upload fields.
- Reduced-motion mode support.

## 11. Data Visualization Rules
- Max 5 primary series per chart before aggregation.
- Always show uncertainty (CI/variance) on predictive outputs.
- Fixed axis conventions for Valence/Arousal to avoid interpretation drift.
- Tooltips include: source run, timestamp, model version, confidence.

## 12. Empty, Loading, Error States
- Empty: explain required input + direct action button.
- Loading: skeleton panels + deterministic progress.
- Error: clear cause, affected module, recovery action ("Re-run preprocessing", "Validate schema").

## 13. Responsive Behavior
- Desktop (≥1280): full 3-segment layout.
- Tablet (900–1279): right panel stack below center.
- Small screens (<900): analysis-first single column; 3D and heatmap switchable tabs.

## 14. Implementation Roadmap
- **Phase 1:** Design tokens + base layout shell + sidebar/navigation.
- **Phase 2:** Panel components and chart theming.
- **Phase 3:** Advanced modules (3D landscape, predictive heatmap, cross-filtering).
- **Phase 4:** Accessibility pass, performance tuning, usability QA.

## 15. Acceptance Criteria
- Users can complete the core workflow (ingest → process → train → predict) from one coherent dashboard.
- Visual style matches dark professional neon system with consistent tokens.
- Cross-panel interactions are synchronized and interpretable.
- Error/uncertainty handling is visible and actionable.
- Interface passes contrast and keyboard accessibility checks.
