# Agentic Manifest: 01 Backend & Data Pipeline

**Role Directive:** You are a Senior Data Architect and ML Engineer.
**Strict Constraint:** Do NOT build API endpoints, Rhino plugins, Grasshopper integrations, or C# code. Do NOT deploy PostgreSQL or Celery. Your sole focus is the local, Python-based Machine Learning training pipeline and data ingestion layer.

---

## 1. Storage & Tech Stack
The backend must operate entirely headlessly (no Streamlit dependencies in `src/`).
* **Language:** Python 3.9+
* **ML Frameworks:** PyTorch, scikit-learn
* **Data Processing:** Pandas, NumPy, SciPy (Welch's PSD, Butterworth, R-peak)
* **Storage Strategy:** Raw data remains as CSVs. All processed data, merged dataframes, and feature tables must be saved locally as **Parquet** files in `data/processed/` for fast retrieval. Use `DuckDB` for any local analytical queries over these Parquet files.

---

## 2. Multi-Experiment Data Ingestion & Cleansing
The pipeline must ingest datasets from `experiment_01`, `experiment_02`, and `experiment_03` simultaneously. Because the schema evolved over time, you must handle legacy data gaps gracefully:

* **Ghost Data:** Aggressively drop any columns containing the word `Unnamed` before merging. Strip trailing whitespaces from all column names (e.g., `"Valence Score by Subject "`).
* **Missing Biometric Targets (Exp 01):** Experiment 01 only has a combined `Score by Subject`. Map this to `NaN` for both Valence and Arousal to trigger the fusion fallback rule (see Section 4).
* **Missing Spatial Features (Exp 01 & 02):** If a room lacks continuous lighting or architectural metrics (e.g., Illuminance, Window Area), impute the missing values with `0.0`. 
* **Missing Categorical Features:** If a room lacks `Type of Space` or `Day or Night`, impute with the string `"Unspecified"`.
* **Missing Demographic Features:** Impute missing `Sleep Hours` with the dataset median.

---

## 3. Spatial Feature Engineering (Strict Schema)
The system is strictly constrained to the physical geometries of the experiments. 

### A. Banned Metrics
You must NEVER ingest, process, or reference the following metrics:
* `UDI` (Useful Daylight Illuminance)
* `sDA` (Spatial Daylight Autonomy)
* `ASE` (Annual Sunlight Exposure)

### B. The 12 Independent Variables (Raw Inputs)
The pipeline must only accept these independent continuous variables:
1. Length (m)
2. Width (m)
3. Height (m)
4. Number of Doors
5. Door Area (m²)
6. Number of Windows
7. Window Area (m²)
8. Daylight Factor (%)
9. Illuminance (lux)
10. CCT (K)
11. Walkable Floor Area (m²)

### C. Categorical Variables (Must be One-Hot Encoded)
1. Day or Night (Day, Night, Unspecified)
2. Type of Space (Bedroom, Living Room, Workplace, Classroom, Cafeteria, Unspecified)
3. Gender (from Subject Data)

### D. Derived Features (Backend Calculated)
The model must autonomously calculate the following from the independent variables:
* Length to Width Ratio (`Length / Width`)
* Floor Area (`Length * Width`)
* Wall Area (`2 * (Length + Width) * Height`)
* Volume (`Length * Width * Height`)
* Door Area to Wall Area Ratio (`Door Area / Wall Area`)
* Window Area to Wall Area Ratio (`Window Area / Wall Area`)
* Walkable Floor to Total Floor Ratio (`Walkable Floor Area / Floor Area`)

---

## 4. Ground Truth Generation: Affective Fusion
The ML model trains on a 2D emotional target (Valence and Arousal). To eliminate subjective recall bias, the pipeline MUST calculate the ground truth using a weighted fusion of biometric data and self-reported survey scores.

### A. The Objective Biometric Layer
* **Valence (EEG):** Calculated using Frontal Alpha Asymmetry (FAA). $FAA = \ln(\alpha_{right}) - \ln(\alpha_{left})$
* **Arousal (ECG):** Calculated using time-domain HRV. Use RMSSD exclusively. Reject SDNN or LF/HF. 

### B. The Fusion Algorithm
Normalize Subjective survey scores to a `[-1, 1]` continuous scale. Calculate the final training target using a tunable parameter $\alpha$ (default `0.6`):
* $Target\_Valence = (\alpha \times FAA) + ((1-\alpha) \times Subjective\_Valence)$
* $Target\_Arousal = (\alpha \times RMSSD) + ((1-\alpha) \times Subjective\_Arousal)$

**CRITICAL Fallback Logic:** If subjective survey scores are missing or `NaN` (e.g., all of Experiment 01), automatically default to 100% objective data ($\alpha = 1.0$) for those specific rows.

### C. Variance Tracking
For every trial, calculate the Euclidean distance between the Objective coordinate and the Subjective coordinate. Save this data to `data/processed/fusion_analysis.parquet`.

---

## 5. Machine Learning Models
* **Primary Architecture:** PyTorch FFNN predicting the 2D Affective Fusion coordinate from the combined spatial feature vector.
* **Baselines:** scikit-learn Random Forest and Support Vector Regression (SVR).
* **Validation:** Use Leave-One-Subject-Out (LOSO) Cross-Validation to ensure the model generalizes to new humans rather than overfitting to specific subjects.