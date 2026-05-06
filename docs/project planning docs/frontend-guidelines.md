# Front-End Guidelines — Predictive Atmospheres

## 1) Purpose and Scope
This document defines implementation guidelines for the user interface across:
- The Streamlit research dashboard (web analytics surface)
- The Rhino plugin UI (CAD design surface)

It consolidates decisions from existing planning documents and the proposed LLM-driven architecture, ensuring consistent visual language, interaction behavior, and performance across both environments.

Related project docs:
- PRD
- Design document (dark theme redesign)
- App flow (researcher + architect journeys)
- Tech stack document

---

## 2) Core Visual Language (Design Tokens)

The design document is the source of truth for all visual tokens. If conflicts appear, this document must follow the values from the dark theme redesign spec.

### 2.1 Token Strategy
Define tokens once and apply them in two places:
- **Web (Streamlit)**: CSS custom properties (`:root` variables)
- **Rhino plugin (C#)**: centralized resource dictionary/constants class

Token naming must be semantic (role-based), not color-name based.
Example:
- `--color-bg-primary` (good)
- `--color-purple` (avoid)

### 2.2 Color Palette
Use this palette as the source of truth for all front-end surfaces.

| Role | Color Name | Hex | Usage |
|---|---|---|---|
| Background (Primary) | Deep Charcoal | #121212 | Main app background, panel base |
| Background (Elevated) | Surface Gray | #222228 | Elevated elements and overlays |
| Surface (Panels) | Panel Gray | #1A1A1A | Cards, panels, module containers |
| Accent 1 (Primary) | Purple 500 | #8A5CFF | Primary actions, active states, wireframes |
| Accent 2 (Deep Purple) | Purple 700 | #5E35D6 | Hover/pressed states, deep traces |
| Accent 3 (Soft Purple) | Purple 300 | #B79CFF | Light emphasis, selected fills |
| Complementary Accent | Yellow-Gold | #D4C94A | Single non-purple emphasis |
| Triadic Accent A | Teal | #2EC4B6 | First non-purple comparison series |
| Triadic Accent B | Orange | #FF9F1C | Second non-purple comparison series |
| Status (Critical) | Orange Critical | #FF9F1C | Critical flags and blocking errors |
| Text (Primary) | Off-White | #E0E0E0 | Main text, chart labels, metrics |
| Text (Secondary) | Muted Gray | #A3A3B2 | Metadata, helper text, non-critical axes |
| Grid/Dividers | Divider Gray | #2A2A36 | Dividers, chart grid lines |

Additional semantic aliases (required):
- Success: #2EC4B6
- Warning: #D4C94A
- Error: #FF9F1C
- Divider/Grid: #2A2A36

### 2.3 Gradients and Glow
- Primary gradient: **Deep Purple → Purple → Soft Purple** (`#5E35D6 → #8A5CFF → #B79CFF`)
- Triadic comparison gradient (only for multi-series comparison): **Teal → Purple → Orange** (`#2EC4B6 → #8A5CFF → #FF9F1C`)
- Secondary overlay gradient: **Purple → Transparent** (`#8A5CFF 20% → transparent`)
- Color-theory rules:
  - Default: purple shades only.
  - Need one non-purple accent: use complementary yellow-gold only.
  - Need two non-purple accents: use triadic teal and orange together.
- Glow usage must be constrained to:
  - Active chart traces
  - Active focus/hover rings
  - Primary call-to-action emphasis

Avoid glow on body text and dense table rows to preserve readability.

### 2.4 Typography
Use modern sans-serif stack:
- Primary: Inter
- Fallbacks: Roboto, SF Pro, Segoe UI, sans-serif

Weights and usage:
- Header: 600 (panel titles, key metrics)
- Body: 400 (descriptions, logs)
- Mono: JetBrains Mono or Fira Code (raw payloads, coordinates, runtime logs)

Recommended type scale:
- H1: 28/36
- H2: 20/28
- H3: 16/24
- Body: 14/22
- Caption: 12/18

---

## 3) Layout and Information Hierarchy

### 3.1 Grid Structure (Web)
- Target a modular dashboard layout with horizontal panel grouping.
- Use multi-column composition; avoid long one-column scroll where possible.
- Preserve these visual zones:
  1. Input/Configuration
  2. Biometric Analysis
  3. Prediction/Feedback

### 3.2 Panel Anatomy
Each panel should follow the same structure:
1. Header row (title + actions)
2. Content area (chart/table/form)
3. Footer meta (updated time, model version, quality badges)

### 3.3 Spacing and Shape
- Corner radius: 14px
- Spacing scale: 4, 8, 12, 16, 24, 32
- Panel border: subtle 1px contrast line using divider token

---

## 4) Component Guidelines

### 4.1 Data Visualization Elements
**Global chart rules**
- Transparent chart backgrounds
- Minimize grid lines; keep only essential axes
- Use divider gray (`#2A2A36`) for grid and off-white for labels; use muted gray (`#A3A3B2`) for secondary axis text
- Always show tooltips with value, unit, timestamp, and data source context

**Bar and scenario charts**
- Use purple-shade gradient for default low-to-high affective intensity
- Use complementary accent only for one highlighted benchmark/baseline
- Use triadic accents only when comparing 3+ series simultaneously
- Keep bars wide enough for legibility in dense comparison states

**Radar chart**
- Stroke: Neon Purple (`#8A5CFF`)
- Fill: Neon Purple at ~20% opacity
- Preserve visible underlying grid

**Valence/Arousal maps**
- Keep fixed axis orientation and ranges across pages
- Overlay confidence region where available

### 4.2 Interactive Controls
**Sliders (room dimensions)**
- Active track: Purple 500 (`#8A5CFF`)
- Inactive track: Surface Gray
- Thumb hover: subtle glow ring

**Buttons**
- Primary actions (for example, Train Model): solid Neon Purple (`#8A5CFF`) + off-white text
- Secondary actions (for example, Export): transparent with accent border
- Disabled state: reduced contrast and no glow

**Progress indicators**
- Prefer circular progress rings for compact, dense panels
- Use stage labels directly below each ring

### 4.3 Feedback and Status
- Success: teal badge (`#2EC4B6`) + concise confirmation text
- Warning: complementary yellow-gold (`#D4C94A`) + clear action prompt
- Error: orange critical (`#FF9F1C`) + exact failure source + retry path
- Never show silent failures

---

## 5) Motion and Interaction Behavior
- Standard transitions: 120–220ms
- Chart transitions: up to 280ms
- Use easing that prioritizes clarity over decoration

Interaction rules:
- Hover: slight elevation and border emphasis
- Active/focus: accent outline + accessible focus ring
- Cross-filtering: selecting one visualization updates all dependent panels
- Preserve interaction continuity (no full page rerender for minor state changes)

---

## 6) Streamlit Implementation Guidelines (Web)

### 6.1 Layout
- Use `st.columns` for primary dashboard zones
- Use `st.expander` for advanced controls and diagnostics
- Keep critical KPIs above fold
- In the ingestion panel, expose two explicit metadata inputs:
  - `experiment_XX_spatial data.csv`
  - `experiment_XX_biometric data.csv`

### 6.2 Theming
- Inject custom CSS using `st.markdown(..., unsafe_allow_html=True)`
- Override Streamlit default palette to tokenized dark theme
- Centralize CSS tokens in one source to avoid drift

### 6.3 State Management
- Use `st.session_state` for:
  - Uploaded data references
  - Split metadata references (`spatial_metadata_path`, `biometric_metadata_path`)
  - Pipeline stage status
  - Model config and selected scenario
  - Cached prediction outputs

### 6.6 Ingestion Validation (Required)
- Validate spatial CSV columns: `Room_ID`, `Length (meter)`, `Width (meter)`, `Height (meter)`
- Validate biometric CSV base columns: `Subject_ID`, `Room_ID`, `Time spent by the subject in the room (seconds)`, `EEG_Filename`
- Validate label columns with backward compatibility:
  - Accept legacy: `Score by Subject_(0-10)`
  - Accept preferred split: `Valence Score by Subject (0-10)` and `Arousal Score by Subject (0-10)`
- Validate relational integrity: every biometric `Room_ID` must exist in spatial CSV
- Treat additional unknown columns as optional parameters and surface them as feature candidates
- Show experiment readiness state:
  - `Planned (Template)` when required numeric values are empty
  - `Ready` when required values are complete
- Block pipeline start for `Planned (Template)` experiments, but allow registration and preview

### 6.4 Performance
- Cache static or heavy resources (models, large tables, mapping assets)
- Debounce expensive chart recalculations
- Show incremental loading states for long operations

### 6.5 Accessibility
- Ensure keyboard reachability for all controls
- Maintain contrast at WCAG AA minimum
- Add textual fallbacks for color-dependent chart meanings

---

## 7) Rhino Plugin UI Guidelines (CAD)

### 7.1 UI Framework and Composition
- Build UI in **Eto.Forms** for cross-platform Rhino support
- Ship as a **dockable panel** (not modal dialog)
- Keep panel persistent through modeling sessions

### 7.2 Runtime Responsiveness
- All model inference calls must be asynchronous
- Never block Rhino UI thread during prediction
- Use cancellation and debouncing for rapid geometry updates

### 7.3 Geometry-Driven Feedback
- Use RhinoCommon listeners for geometry modification events
- Recompute required spatial descriptors on change
- Update prediction UI with clear timestamp and confidence

### 7.4 Viewport Overlay Strategy
- Use display pipeline overlays (for example, DisplayConduit) for temporary heatmaps
- Avoid baking analysis geometry into the user model by default
- Allow explicit user action to snapshot/export overlays

---

## 8) Cross-Surface Consistency Rules
Apply these same UX rules to Streamlit and Rhino panels:
- Same semantic token names and status colors
- Same chart legend ordering and units
- Same Valence/Arousal axis conventions
- Same model version label format
- Same warning/error wording patterns

This ensures that researchers and architects interpret results consistently across tools.

---

## 9) Content and Microcopy Guidelines
- Prefer concise, action-oriented labels:
  - "Upload Spatial CSV"
  - "Upload Biometric CSV"
  - "Run Preprocessing"
  - "Train Model"
  - "Export ONNX"
  - "Apply Geometry"
- Error copy format:
  - What failed
  - Why it failed (if known)
  - What user should do next

Avoid vague messages such as "Something went wrong" without context.

---

## 10) QA Checklist (Front-End)

### Visual QA
- Dark theme tokens correctly applied across all panels
- Purple-first gradient and glow usage is consistent and restrained
- Complementary/triadic accents follow the color-theory usage rules
- No low-contrast text in dense data sections

### Functional QA
- Streamlit state persists across rerenders
- Rhino panel remains responsive during inference
- Cross-panel updates are synchronized and deterministic

### Data Viz QA
- Axis labels and units always visible
- Tooltip values match source data
- Confidence/uncertainty indicators shown where applicable

### Accessibility QA
- Keyboard navigation complete
- Focus indicators visible
- Color-only communication avoided

---

## 11) Recommended Deliverables for Implementation
1. Token registry (web CSS + C# constants)
2. Shared chart style specification
3. Component library checklist (buttons, sliders, ring progress, cards)
4. Streamlit theme stylesheet and layout templates
5. Rhino docked panel UI spec and async inference pattern
6. Front-end QA test sheet

---

## 12) Definition of Done (Front-End)
- Both Streamlit and Rhino UIs implement the same core visual language.
- Primary workflows are fully operable without UI blocking.
- Charts and controls meet readability and accessibility targets.
- A researcher and architect can interpret outputs consistently without retraining on interface behavior.
