import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui.theme import style_figure, panel_header, PALETTE, render_hero
from frontend.ui.data_utils import load_parquet_data

def render_page():
    render_hero(
        "Demographic Insights",
        "Distribution of target Valence and Arousal segmented by Age, Gender, and Sleep patterns.",
        kicker="Demographics",
        compact=True
    )
    
    df = load_parquet_data()
    if df is None or df.empty:
        st.error("No data available to display demographic insights.")
        return
    
    required_cols = ["age", "Sleep_Hours", "fused_valence", "fused_arousal"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        return
    
    dem_df = df.copy()
    # Process Sleep Bracket
    dem_df["Sleep Bracket"] = pd.cut(
        dem_df["Sleep_Hours"].clip(lower=0, upper=24),
        bins=[0, 6, 8, 24],
        labels=["<6 hrs", "6-8 hrs", ">8 hrs"],
        include_lowest=True
    )
    if dem_df["Sleep Bracket"].isna().any():
        st.warning(f"Warning: {dem_df['Sleep Bracket'].isna().sum()} records have missing or invalid sleep hour values.")
    if "gender_Male" in dem_df.columns and "gender_Female" in dem_df.columns:
        dem_df["Gender"] = dem_df.apply(lambda r: "Male" if r["gender_Male"]==1 else ("Female" if r["gender_Female"]==1 else "Unknown"), axis=1)
    else:
        dem_df["Gender"] = "Unknown"
        
    # Process Age Bracket
    dem_df["Age Bracket"] = pd.cut(dem_df["age"], bins=[0, 25, 35, 50, 100], labels=["<25", "25-35", "35-50", ">50"])
    
    # Process Sleep Bracket
    dem_df["Sleep Bracket"] = pd.cut(dem_df["Sleep_Hours"], bins=[0, 6, 8, 24], labels=["<6 hrs", "6-8 hrs", ">8 hrs"])
    
    demographic_filter = st.radio("Select Demographic Segment:", ["Gender", "Age Bracket", "Sleep Bracket"], horizontal=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        panel_header("Valence Distribution", "Demographics")
        fig_v = px.violin(
            dem_df, x=demographic_filter, y="fused_valence", 
            color=demographic_filter, box=True, points="all",
            color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"], PALETTE["border"]]
        )
        style_figure(fig_v, f"Target Valence by {demographic_filter}", height=450)
        fig_v.update_layout(showlegend=False)
        st.plotly_chart(fig_v, use_container_width=True)
        
    with col2:
        panel_header("Arousal Distribution", "Demographics")
        fig_a = px.violin(
            dem_df, x=demographic_filter, y="fused_arousal", 
            color=demographic_filter, box=True, points="all",
            color_discrete_sequence=[PALETTE["accent"], PALETTE["accent_2"], PALETTE["muted"], PALETTE["border"]]
        )
        style_figure(fig_a, f"Target Arousal by {demographic_filter}", height=450)
        fig_a.update_layout(showlegend=False)
        st.plotly_chart(fig_a, use_container_width=True)
