import streamlit as st
import streamlit.components.v1 as components

def render_system_architecture():
    st.subheader("Scientific ML Architecture & Data Pipelines")
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
  <style>
    body { 
        background-color: #131314; 
        margin: 0; 
        padding: 0;
        display: flex; 
        align-items: center; 
        justify-content: flex-start;
        height: 100vh; 
        width: 100vw;
        overflow-x: auto;
        overflow-y: hidden; 
        font-family: "Source Sans Pro", sans-serif; 
    }
    
    .mermaid { 
        display: flex; 
        align-items: center; 
        justify-content: flex-start; 
        height: 100%; 
        padding: 0 40px; 
    }
    
    /* Allow SVG to overflow horizontally to maintain scale relative to height */
    .mermaid svg { 
        height: 85vh !important; 
        width: auto !important; 
        max-width: none !important;
        min-width: max-content !important;
    }
    
    /* Mermaid Subgraph Overrides */
    .cluster rect { fill: #1E1F20 !important; stroke: #75b6da !important; stroke-width: 2px !important; rx: 12px !important; ry: 12px !important; }
    .cluster-label text, .cluster text { fill: #FAFAFA !important; font-size: 16px !important; font-weight: 600 !important; font-family: sans-serif !important; }
    
    /* Hide Mermaid's native boxes so our custom HTML renders cleanly */
    .node rect, .node circle, .node polygon, .node path { fill: transparent !important; stroke: transparent !important; }
    .label { color: #FAFAFA !important; }

    /* Custom HTML Node Design */
    .node-wrapper { display: flex; flex-direction: column; align-items: center; text-align: center; width: 140px; }
    .icon-circle {
      width: 55px; height: 55px;
      border: 2px solid #FFFFFF; border-radius: 50%;
      background-color: #262730;
      display: flex; justify-content: center; align-items: center;
      margin-bottom: 10px; transition: all 0.2s ease;
    }
    .node-wrapper:hover .icon-circle { border-color: #75b6da; transform: scale(1.1); box-shadow: 0 0 15px rgba(117, 182, 218, 0.4); }
    .material-icons { font-size: 28px; color: #FFFFFF; }
    .node-label { font-size: 13px; line-height: 1.3; color: #FAFAFA; font-weight: 500; }
  </style>
</head>
<body>
  <div class="mermaid">
  %%{init: {"theme": "base", "themeVariables": { "lineColor": "#FFFFFF", "fontFamily": "sans-serif", "clusterBkg": "#1E1F20", "clusterBorder": "#75b6da", "textColor": "#FAFAFA" }, "flowchart": {"htmlLabels": true, "nodeSpacing": 60, "rankSpacing": 90} } }%%
  graph LR
    classDef default fill:none,stroke:none;

    subgraph Data_Collection [1. Environment & Ingestion]
        Spat["<div class='node-wrapper' title='18-Dimensional Feature Vector: 11 Numeric (Length, Width, etc.) + 7 One-Hot Encoded Categories'><div class='icon-circle'><span class='material-icons'>architecture</span></div><div class='node-label'>Spatial Data<br>(18 Features)</div></div>"]
        VR["<div class='node-wrapper' title='Subjects experience the spatial configurations in Virtual Reality'><div class='icon-circle'><span class='material-icons'>visibility</span></div><div class='node-label'>VR Space<br>Exposure</div></div>"]
        Subj["<div class='node-wrapper' title='Self-reported Valence and Arousal scores from the subject'><div class='icon-circle'><span class='material-icons'>assignment</span></div><div class='node-label'>Subjective<br>Scores</div></div>"]
    end

    subgraph Signal_Processing [2. Biometric Pipelines]
        EEG["<div class='node-wrapper' title='Raw Electroencephalography from channels F3 (Left Frontal) and F4 (Right Frontal) @ 256Hz'><div class='icon-circle'><span class='material-icons'>psychology</span></div><div class='node-label'>EEG (F3/F4)</div></div>"]
        ECG["<div class='node-wrapper' title='Raw Electrocardiography for heart rate variability analysis @ 256Hz'><div class='icon-circle'><span class='material-icons'>favorite</span></div><div class='node-label'>ECG Signal</div></div>"]

        E_Trunc["<div class='node-wrapper' title='T+0s to T+50s (12,800 samples) | Butterworth High-pass Filter (1.0Hz, order 4)'><div class='icon-circle'><span class='material-icons'>content_cut</span></div><div class='node-label'>Truncation &<br>HP Filter</div></div>"]
        Welch["<div class='node-wrapper' title='Welch’s Method: Extracts Power Spectral Density for Delta, Theta, Alpha, Beta, Gamma bands'><div class='icon-circle'><span class='material-icons'>waves</span></div><div class='node-label'>Welch PSD</div></div>"]
        FAA["<div class='node-wrapper' title='Frontal Alpha Asymmetry: ln(Alpha Right) - ln(Alpha Left). Clipped to [-1.0, 1.0] for Objective Valence'><div class='icon-circle'><span class='material-icons'>functions</span></div><div class='node-label'>FAA Comp.<br>(Valence)</div></div>"]

        C_Trunc["<div class='node-wrapper' title='T+0s to T+50s | SOS Butterworth Band-pass Filter (0.5Hz - 5.0Hz)'><div class='icon-circle'><span class='material-icons'>timeline</span></div><div class='node-label'>Truncation &<br>BP Filter</div></div>"]
        RPeak["<div class='node-wrapper' title='Scipy find_peaks: Extract R-peaks and compute RR-Intervals (ms) with outlier rejection'><div class='icon-circle'><span class='material-icons'>monitor_heart</span></div><div class='node-label'>R-Peak<br>Detection</div></div>"]
        RMSSD["<div class='node-wrapper' title='Root Mean Square of Successive Differences: RMSSD = sqrt(mean(valid_diffs^2))'><div class='icon-circle'><span class='material-icons'>calculate</span></div><div class='node-label'>RMSSD</div></div>"]
        Arousal["<div class='node-wrapper' title='Objective Arousal = 1.0 - (RMSSD / 50.0). Clipped to [-1.0, 1.0]'><div class='icon-circle'><span class='material-icons'>speed</span></div><div class='node-label'>Arousal<br>Mapping</div></div>"]

        Fusion["<div class='node-wrapper' title='Multimodal Fusion: Target = (0.6 * Objective) + (0.4 * Subjective)'><div class='icon-circle'><span class='material-icons'>merge_type</span></div><div class='node-label'>Affective Fusion<br>(&alpha; = 0.6)</div></div>"]
        GT["<div class='node-wrapper' title='Parquet file serving as the ground-truth dataset for Model Training'><div class='icon-circle'><span class='material-icons'>storage</span></div><div class='node-label'>Ground Truth<br>Tensor</div></div>"]
    end
    
    subgraph ML_Architecture [3. SpatialFFNN Topology]
        L1["<div class='node-wrapper' title='Linear(18 &rarr; 64) &rarr; BatchNorm &rarr; ReLU &rarr; Dropout(0.3)'><div class='icon-circle'><span class='material-icons'>layers</span></div><div class='node-label'>Linear L1</div></div>"]
        L2["<div class='node-wrapper' title='Linear(64 &rarr; 128) &rarr; BatchNorm &rarr; ReLU &rarr; Dropout(0.2)'><div class='icon-circle'><span class='material-icons'>layers</span></div><div class='node-label'>Linear L2</div></div>"]
        L3["<div class='node-wrapper' title='Linear(128 &rarr; 64) &rarr; BatchNorm'><div class='icon-circle'><span class='material-icons'>layers</span></div><div class='node-label'>Linear L3</div></div>"]
        Res["<div class='node-wrapper' title='Residual Addition (L1 Output + L3 Output) &rarr; ReLU &rarr; Dropout(0.1)'><div class='icon-circle'><span class='material-icons'>merge_type</span></div><div class='node-label'>Residual Add</div></div>"]
        L4["<div class='node-wrapper' title='Linear(64 &rarr; 32) &rarr; ReLU'><div class='icon-circle'><span class='material-icons'>layers</span></div><div class='node-label'>Linear L4</div></div>"]
        Out["<div class='node-wrapper' title='Linear(32 &rarr; 2) &rarr; Tanh Activation'><div class='icon-circle'><span class='material-icons'>output</span></div><div class='node-label'>Output Layer</div></div>"]
        Pred["<div class='node-wrapper' title='Predicted Vector: [Valence, Arousal] &isin; [-1, 1]'><div class='icon-circle'><span class='material-icons'>adjust</span></div><div class='node-label'>Predicted [V, A]</div></div>"]
    end

    %% Connections
    Spat -.-> VR
    VR -.-> EEG
    VR -.-> ECG
    VR -.-> Subj

    EEG --> E_Trunc --> Welch --> FAA --> Fusion
    ECG --> C_Trunc --> RPeak --> RMSSD --> Arousal --> Fusion
    Subj --> Fusion
    
    Fusion ===> GT
    
    GT ===> L1
    L1 --> L2 --> L3 --> Res
    L1 -.->|Skip Connection| Res
    Res --> L4 --> Out --> Pred
  </div>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });
  </script>
</body>
</html>
"""
    
    components.html(html_template, height=900, scrolling=True)
