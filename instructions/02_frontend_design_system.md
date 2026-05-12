# Agentic Manifest: 02 Frontend & Design System

**Role Directive:** You are a Senior UI/UX Engineer and Data Visualization Expert.
**Strict Constraint:** Your sole focus is building the `/frontend` using Streamlit and Plotly. Do NOT write React, Vue, HTML/CSS for external websites, or C# for Rhino. Do not use Streamlit's default light theme.

---

## 1. Global Theming & CSS Tokens

The application must use a strict, custom Dark Blue theme. Do not use default Streamlit colors or the Plotly default colorway.

### A. Color Palette (Hex Codes)

- **Background (Base):** `#041122` (Deepest Navy)
- **Surface (Cards/Panels):** `#0A2240` (Elevated Navy)
- **Accent 1 (Primary Action/Active):** `#1C5B99` (Mid-tone Blue)
- **Accent 2 (Highlight/Glow):** `#4287C6` (Bright Blue)
- **Accent 3 (Muted/Inactive):** `#11365E` (Dark Blue)
- **Text Primary:** `#F4F8FC` (Ice Blue / Off-White)
- **Text Secondary:** `#8AA4C1` (Muted Blue-Gray)
- **Dividers/Gridlines:** `#0F2D53`
- **Target/Fused Point (Charts only):** `#FFFFFF`

### B. Typography Injection

You must inject a `style.css` file via `st.markdown(unsafe_allow_html=True)` to enforce these exact fonts:

- **Primary Font (`Google Sans Flex`):** Must be used for all headers (`h1`, `h2`, `h3`), standard paragraph text, UI labels, and Streamlit component labels.
- **Secondary Font (`Cutive Mono`):** Must be used strictly for quantitative data: numeric outputs, biometric arrays, metric deltas (e.g., $\Delta$ RMSSD), table data, and Plotly axis tick labels.

---

## 2. Layout & Interaction Rules

- **Modularity:** Use `st.columns` for horizontal panel grouping. Keep critical KPIs above the fold.
- **State Management:** Use `st.session_state` to persist uploaded data paths, model configuration, and selected scenarios to prevent UI resets on interaction.
- **Component Styling:** Wrap biometric readouts and spatial parameters in custom HTML/CSS containers using the Surface color (`#0A2240`) and a 1px solid border using the Divider color (`#0F2D53`).
- **Error Boundaries:** Never fail silently. If a backend file (like `fusion_analysis.parquet`) is missing, render a styled warning box using a complementary accent color (e.g., Gold/Orange) instructing the user to run the training pipeline.

---

## 3. Plotly Visualization Strict Guidelines

Every Plotly chart (`plotly.graph_objects` or `plotly.express`) must adhere to these overrides:

- **Backgrounds:** `paper_bgcolor` and `plot_bgcolor` must be set to `rgba(0,0,0,0)` (transparent) so the Streamlit surface color shows through.
- **Gridlines:** Set `showgrid=True`, but strictly color them using the Divider token (`#0F2D53`). Remove zero-lines unless plotting the Circumplex origin.
- **Traces & Markers:**
  - Single-series data must use Accent 1 (`#1C5B99`).
  - Continuous data (heatmaps, 3D meshes) must use a custom colorscale ranging from the Background token (`#041122`) to the Text Primary token (`#F4F8FC`).
  - **DO NOT** use Plotly's default Viridis, Plasma, or standard categorical colorways.
- **Typography:** Override the `font.family` in the Plotly layout. Use `Google Sans Flex` for chart titles and axis titles. Use `Cutive Mono` for hover labels and axis ticks.
