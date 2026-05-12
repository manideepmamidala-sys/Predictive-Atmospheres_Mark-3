import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui.theme import style_figure, panel_header, PALETTE
from frontend.ui.data_utils import load_parquet_data

def render_page():
    st.title("Demographic Insights")
    st.markdown("Distribution of target Valence and Arousal segmented by Age, Gender, and Sleep patterns.")
    
    df = load_parquet_data()
    dem_df = df.copy()
    
    # Process Gender
    if "gender_Male" in dem_df.columns and "gender_Female" in dem_df.columns:
        dem_df["Gender"] = dem_df.apply(lambda r: "Male" if r["gender_Male"]==1 else ("Female" if r["gender_Female"]==1 else "Unknown"), axis=1)
    else:
        dem_df["Gender"] = "Unknown"
        
    # Process Age Bracket
    dem_df["Age Bracket"] = pd.cut(dem_df["age"], bins=[0, 25, 35, 50, 100], labels=["<25", "25-35", "35-50", ">50"])
    
    # Process Sleep Bracket
    dem_df["Sleep Bracket"] = pd.cut(dem_df["Sleep_Hours"], bins=[0, 6, 8, 24], labels=["<6 hrs", "6-8 hrs", ">8 hrs"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        panel_header("Valence Distribution", "Demographics")
        fig_v_gen = px.violin(dem_df, x="Gender", y="fused_valence", color="Gender", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
        style_figure(fig_v_gen, "Target Valence by Gender", height=380)
        fig_v_gen.update_layout(showlegend=False)
        st.plotly_chart(fig_v_gen, use_container_width=True)
        
        fig_v_age = px.violin(dem_df, x="Age Bracket", y="fused_valence", color="Age Bracket", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"], PALETTE["border"]])
        style_figure(fig_v_age, "Target Valence by Age", height=380)
        fig_v_age.update_layout(showlegend=False)
        st.plotly_chart(fig_v_age, use_container_width=True)
        
        fig_v_sleep = px.violin(dem_df, x="Sleep Bracket", y="fused_valence", color="Sleep Bracket", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
        style_figure(fig_v_sleep, "Target Valence by Sleep", height=380)
        fig_v_sleep.update_layout(showlegend=False)
        st.plotly_chart(fig_v_sleep, use_container_width=True)
        
    with col2:
        panel_header("Arousal Distribution", "Demographics")
        fig_a_gen = px.violin(dem_df, x="Gender", y="fused_arousal", color="Gender", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
        style_figure(fig_a_gen, "Target Arousal by Gender", height=380)
        fig_a_gen.update_layout(showlegend=False)
        st.plotly_chart(fig_a_gen, use_container_width=True)
        
        fig_a_age = px.violin(dem_df, x="Age Bracket", y="fused_arousal", color="Age Bracket", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"], PALETTE["border"]])
        style_figure(fig_a_age, "Target Arousal by Age", height=380)
        fig_a_age.update_layout(showlegend=False)
        st.plotly_chart(fig_a_age, use_container_width=True)
        
        fig_a_sleep = px.violin(dem_df, x="Sleep Bracket", y="fused_arousal", color="Sleep Bracket", box=True, color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"]])
        style_figure(fig_a_sleep, "Target Arousal by Sleep", height=380)
        fig_a_sleep.update_layout(showlegend=False)
        st.plotly_chart(fig_a_sleep, use_container_width=True)
