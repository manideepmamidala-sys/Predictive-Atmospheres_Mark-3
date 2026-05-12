# Agentic Manifest: 03 Execution Roadmap (Multi-Experiment)

**Role Directive:** You are a Python Data Engineer and Full-Stack Streamlit Developer.
**Strict Constraint:** Execute ONLY the tasks in this roadmap. Ignore any legacy documentation requesting Rhino plugins, C#, Eto.Forms, ONNX Runtime, or PostgreSQL deployments. Do NOT write speculative code.

---

## Phase 1: Robust Multi-Experiment Data Ingestion
You must write a resilient data loader in `src/data/data_loader.py` that ingests and unifies `experiment_01`, `experiment_02`, and `experiment_03`.

**Step 1: Unify and Cleanse Biometric Data**
* Load the three biometric CSVs.
* Strip trailing whitespaces from all column names (e.g., `"Valence Score by Subject "` -> `"Valence Score by Subject"`).
* **Missing Target Handling:** For Experiment 01, which only has `Score by Subject`, map this to `NaN` for both Valence and Arousal so the Fusion engine knows to fall back to 100% objective data.
* Concatenate them into a single `bio_df`. Fill missing `Sleep Hours` with the dataset median.

**Step 2: Unify and Cleanse Spatial Data**
* Load the three spatial CSVs.
* Drop any columns named `Unnamed`.
* Concatenate them into a single `spatial_df`. 
* **Imputation Rule:** Fill missing continuous independent variables (e.g., Illuminance, Window Area for Exp 01) with `0.0`. Fill missing categorical variables (e.g., `Type of Space` for Exp 01 and 02) with the string `"Unspecified"`.

**Step 3: The Grand Join**
* Load `Subject Data.csv`. Merge it with `bio_df` on `Subject_ID`.
* Merge the resulting dataframe with `spatial_df` on `Room_ID`.
* Drop any rows where `Room_ID` or `Subject_ID` is `NaN`.
* One-hot encode the categorical variables (`Type of Space`, `Day or Night`, `gender`).

---

## Phase 2: Affective Fusion Target Calculation
In `src/data/emotion_engine.py`, execute the Multimodal Affective Fusion on the newly unified dataframe.
* Calculate `FAA` (Valence) and `RMSSD` (Arousal) from the raw EEG/ECG arrays for the 50-second truncated window.
* Fetch the "Valence Score by Subject" and "Arousal Score by Subject".
* Compute the final targets: $Target = (\alpha \times Objective) + ((1-\alpha) \times Subjective)$ using $\alpha = 0.6$.
* **Fallback execution:** If the Subjective score is `NaN` (as it will be for Experiment 01), automatically set $\alpha = 1.0$ for that row.
* Calculate the Euclidean variance ($\Delta$) between the Objective and Subjective coordinates.
* Save the fully merged, fused, and cleansed dataframe to `data/processed/fusion_analysis.parquet`.

---

## Phase 3: The Infographics Dashboard (`/frontend/ui/infographics.py`)
Build the Streamlit application applying the Dark Blue visual system defined in `02_frontend_design_system.md`.

**Tab 1: Affective Fusion Map**
* Render a 2D Plotly Scatter Plot (Circumplex Model).
* Plot Subjective Score (Light Blue Square) and Objective Biometric Score (Mid-Blue Circle).
* Draw a dashed error line connecting them, terminating at the Final Target (White Star).
* Display average $\Delta Valence$ and $\Delta Arousal$ in CSS-styled metric cards.

**Tab 2: Spatial Correlator**
* Render a Plotly Heatmap mapping the 12 Independent Spatial Features against the Final Target Valence and Arousal. Use a continuous Navy-to-White colorscale.

**Tab 3: Demographic Modifiers**
* Render Plotly Violin plots displaying the distribution of Target Valence/Arousal, segmented by `gender`, `age` brackets, and `Sleep Hours`.

**Tab 4: Environmental Modifiers**
* Render grouped Plotly Box plots comparing emotional targets strictly grouped by `Day or Night` and `Type of Space` (Include "Unspecified" as a baseline).

---

## Execution Constraints
1. Create the files, write the python code, and execute the backend data pipeline first.
2. Verify the `fusion_analysis.parquet` exists and contains no `NaN` values in target columns.
3. Only after the data is verified, build the Streamlit UI and wire it to the Parquet file.