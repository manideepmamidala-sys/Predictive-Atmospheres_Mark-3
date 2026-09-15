# Predictive Atmospheres: Full-Stack Execution Protocol

**Primary Directive:** Execute a production-grade, full-stack web deployment mapping the "Predictive Atmospheres" architectural thesis. Enforce strict typescript typing, highly optimized API routing, and high-fidelity, minimalist orthographic styling matching the thesis visual identity.

---

## 1.0 System Architecture

*   **Frontend:** React 18, Vite, TypeScript, Vercel (Hosting).
*   **Backend:** Python 3.10, FastAPI, `scikit-learn`, Render/Railway (Hosting).
*   **State Management:** Zustand (debounced inputs).
*   **Animation & Routing:** Framer Motion (scroll-driven narrative), React Router.
*   **Data Visualization:** `plotly.js-basic-dist` + `react-plotly.js`.
*   **Styling:** Tailwind CSS. Strict constraints: Background `#0E1117`, Text `#FFFFFF`, Borders `#FFFFFF` at 20% opacity. Zero border-radius (`rounded-none`).

---

## 2.0 Backend Protocol (FastAPI)

**Task:** Convert the local `api.py` into a robust, stateless cloud service.

### 2.1 Dependencies
*   Create `requirements.txt`: `fastapi`, `uvicorn`, `pydantic`, `scikit-learn`, `joblib`, `numpy`, `pandas`.

### 2.2 Data Validation (Pydantic)
*   Define the `SpatialVector` payload strictly:
    *   `length_m`: float
    *   `width_m`: float
    *   `height_m`: float
    *   `num_doors`: int
    *   `door_area_m2`: float
    *   `num_windows`: int
    *   `window_area_m2`: float
    *   `daylight_factor_pct`: float
    *   `illuminance_lux`: float
    *   `cct_k`: float
    *   `walkable_floor_area_m2`: float
    *   `room_volume_m3`: float
    *   `space_use_type`: string

### 2.3 Endpoint Logic
*   **POST `/predict`:**
    *   Ingest `SpatialVector`.
    *   Load serialized Random Forest `.joblib` model (ensure model is cached in memory on startup, do not load per request).
    *   Execute `.predict()`.
    *   Return JSON: `{"neuro_score": float, "valence": float, "arousal": float, "confidence_pct": float, "atmospheric_label": string}`.
*   **POST `/inverse-optimize`:**
    *   Ingest `TargetNeuroScore` (float).
    *   Execute optimization loop to return closest matching `SpatialVector`.

### 2.4 Security
*   Implement `CORSMiddleware`.
*   Restrict `allow_origins` strictly to the production Vercel URL. Reject all wildcard (`*`) origins.

---

## 3.0 Frontend Protocol (Vite + TypeScript)

**Task:** Build the interactive, narrative-driven client interface.

### 3.1 Global CSS & Tailwind Configuration
*   Define base styles in `index.css`:
    ```css
    body { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    ```
*   Extend Tailwind theme:
    ```javascript
    theme: {
      extend: {
        colors: { background: '#0E1117', foreground: '#FFFFFF', border: 'rgba(255, 255, 255, 0.2)' }
      }
    }
    ```

### 3.2 State Management (Zustand)
*   Create `usePlatformStore.ts`.
*   Define state variables for the 11 spatial inputs and the 5 output metrics.
*   Implement a `fetchPrediction` async action.
*   **Critical:** Wrap the `fetchPrediction` trigger in a 150ms debounce utility to prevent API flooding during slider manipulation.

---

## 4.0 Component Architecture & Narrative Flow

Construct the application as a continuous, scroll-driven funnel transitioning from theoretical research to the live interactive tool.

### 4.1 `HeroSection.tsx`
*   **Visual:** Full-bleed `<video autoPlay muted loop playsInline>` of the thesis teaser.
*   **Overlay:** Project title and the primary thesis statement: "Transitioning architecture from subjective intuition to objective predictability."
*   **Action:** Scroll indicator chevron pointing down.

### 4.2 `ResearchNarrative.tsx`
*   **Mechanic:** Use `framer-motion` `useInView` to fade elements in as they enter the viewport.
*   **Content Modules:**
    1.  *The Static Problem:* 90% time indoors vs. lack of physiological metrics.
    2.  *Methodology:* Orthographic diagram mapping the VR space $\rightarrow$ EEG/ECG extraction $\rightarrow$ V.A.D. Model mapping.

### 4.3 `FindingsVisualizer.tsx`
*   **Mechanic:** Interactive Plotly charts.
*   **Chart 1:** Target (Fused) Density Field. `mode: 'markers'`, mapped on a 2D grid (-1 to 1).
*   **Chart 2:** Random Forest Feature Contributions. Horizontal bar chart (Window Area, Walkable Area, etc.).

### 4.4 `InteractiveStudio.tsx` (The Core Platform)
*   **Error Handling:** Include a global `ErrorBanner.tsx`. Catch `500` errors and display them in a full-width red (`#EF4444`) Tailwind banner at the top of the UI. Catch `422` validation errors and display them as inline red text immediately below the corresponding slider inputs.
*   **Layout:** Two-column CSS Grid. `gap-8`, divided by a thin `border-r border-white/20`.
*   **Left Column (Inputs):**
    *   Grouped sliders: *Geometry*, *Daylight*, *Openings*, *Space Details*.
    *   Toggle for "AI Co-Design" (Inverse Optimization).
*   **Right Column (Outputs):**
    *   Large numeric readouts for `Predicted Neuro-Score` and `Confidence`.
    *   Plotly 2D Scatter chart mapping the output `Valence` (X) and `Arousal` (Y) against the 4 quadrants (Activated Stress, Engaged Positive, Low-Energy Negative, Calm Positive).
    *   Orthographic styling for all readouts.

---

## 5.0 Deployment Protocol

### 5.1 Backend Deployment (Render/Railway)
*   Connect the repository to the hosting provider.
*   Set build command: `pip install -r requirements.txt`.
*   Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`.
*   Extract the generated live URL.

### 5.2 Frontend Deployment (Vercel)
*   Inject the Backend URL into the Vite environment variables: `VITE_API_URL=https://<backend-url>.com`.
*   Deploy via Vercel.
*   Verify API CORS handshakes correctly with the finalized Vercel domain.