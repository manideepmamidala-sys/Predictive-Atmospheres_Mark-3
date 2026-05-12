import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui.theme import style_figure, panel_header, PALETTE
from frontend.ui.data_utils import load_parquet_data

def render_page():
    st.title("Spatial Correlator")
    st.markdown("Heatmaps correlating independent spatial inputs with biometric affective targets.")
    
    df = load_parquet_data()
    
    features = [
        "Length_m", "Width_m", "Height_m", "Num_Doors", "Door_Area_m2", 
        "Num_Windows", "Window_Area_m2", "Daylight_Factor_pct", 
        "Illuminance_lux", "CCT_K", "Walkable_Floor_Area_m2"
    ]
    features = [f for f in features if f in df.columns]
    
    if not features:
        st.warning("Spatial features not found in dataset.")
        return
        
    corr_df = df[features + ["fused_valence", "fused_arousal"]].corr().loc[features, ["fused_valence", "fused_arousal"]]
    
    panel_header("Feature Correlation", "Heatmap")
    
    fig = px.imshow(
        corr_df, 
        labels=dict(x="Affective Target", y="Spatial Feature", color="Correlation"),
        x=["Valence", "Arousal"], 
        y=features,
        color_continuous_scale=[[0, PALETTE["bg"]], [1, PALETTE["target"]]]
    )
                     
    style_figure(fig, "Spatial vs Affective Correlation", height=600)
    st.plotly_chart(fig, use_container_width=True)
