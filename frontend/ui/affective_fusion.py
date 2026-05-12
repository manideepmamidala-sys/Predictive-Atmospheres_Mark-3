import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from frontend.ui.theme import style_figure, panel_header
from frontend.ui.data_utils import load_parquet_data

def render_page():
    st.title("Affective Fusion Map")
    st.markdown("Circumplex model illustrating the variance (Δ) between subjective and objective emotional states.")
    
    df = load_parquet_data()
    
    avg_delta_v = df["delta_valence"].mean()
    avg_delta_a = df["delta_arousal"].mean()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">Average Δ Valence</div><div class="metric-card-val">{avg_delta_v:.3f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">Average Δ Arousal</div><div class="metric-card-val">{avg_delta_a:.3f}</div></div>', unsafe_allow_html=True)
        
    panel_header("Point A to Point B Variance Analysis", "Circumplex")
    fig = go.Figure()
    
    for idx, row in df.iterrows():
        if pd.notna(row['subjective_valence']) and pd.notna(row['subjective_arousal']):
            fig.add_trace(go.Scatter(
                x=[row['subjective_valence'], row['objective_valence'], row['fused_valence']],
                y=[row['subjective_arousal'], row['objective_arousal'], row['fused_arousal']],
                mode='lines',
                line=dict(color="#0F2D53", width=1, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Subjective
    fig.add_trace(go.Scatter(
        x=df['subjective_valence'], y=df['subjective_arousal'],
        mode='markers', marker=dict(color="#4287C6", symbol='square', size=8),
        name='Subjective Score'
    ))
    
    # Objective
    fig.add_trace(go.Scatter(
        x=df['objective_valence'], y=df['objective_arousal'],
        mode='markers', marker=dict(color="#1C5B99", symbol='circle', size=8),
        name='Objective Biometric'
    ))
    
    # Fused Target
    fig.add_trace(go.Scatter(
        x=df['fused_valence'], y=df['fused_arousal'],
        mode='markers', marker=dict(color="#FFFFFF", symbol='star', size=12),
        name='Final Target'
    ))
    
    style_figure(fig, "Affective Variance Map", height=650)
    fig.update_xaxes(zeroline=True, zerolinecolor="#0F2D53", zerolinewidth=2, range=[-1.1, 1.1])
    fig.update_yaxes(zeroline=True, zerolinecolor="#0F2D53", zerolinewidth=2, range=[-1.1, 1.1])
    st.plotly_chart(fig, use_container_width=True)
