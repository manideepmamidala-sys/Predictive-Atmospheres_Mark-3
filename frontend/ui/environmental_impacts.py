import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui.theme import style_figure, panel_header, PALETTE
from frontend.ui.data_utils import load_parquet_data

def render_page():
    st.title("Environmental Impacts")
    st.markdown("Comparisons of emotional targets grouped strictly by Time of Day and Type of Space.")
    
    df = load_parquet_data()
    env_df = df.copy()
    
    def get_dn(r):
        if r.get("Day_or_Night_Day", 0) == 1: return "Day"
        if r.get("Day_or_Night_Night", 0) == 1: return "Night"
        return "Unspecified"
    env_df["Time of Day"] = env_df.apply(get_dn, axis=1)
    
    space_types = ["Bedroom", "Living Room", "Workplace", "Classroom", "Cafeteria", "Unspecified"]
    def get_space(r):
        for s in space_types:
            if r.get(f"Type_of_Space_{s}", 0) == 1:
                return s
        return "Unspecified"
    env_df["Type of Space"] = env_df.apply(get_space, axis=1)
    
    panel_header("Valence vs Environment", "Condition Analysis")
    fig4_v = px.box(env_df, x="Type of Space", y="fused_valence", color="Time of Day", color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
    style_figure(fig4_v, "Target Valence grouped by Time & Space Type", height=500)
    st.plotly_chart(fig4_v, use_container_width=True)
    
    panel_header("Arousal vs Environment", "Condition Analysis")
    fig4_a = px.box(env_df, x="Type of Space", y="fused_arousal", color="Time of Day", color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
    style_figure(fig4_a, "Target Arousal grouped by Time & Space Type", height=500)
    st.plotly_chart(fig4_a, use_container_width=True)
