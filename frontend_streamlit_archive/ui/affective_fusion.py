import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from frontend_streamlit_archive.ui.theme import style_figure, panel_header, render_hero
from frontend_streamlit_archive.ui.data_utils import load_parquet_data

def render_page():
    render_hero(
        "Affective Fusion Map",
        "Circumplex model illustrating the variance (Δ) between subjective and objective emotional states.",
        kicker="Infographic",
        compact=True
    )
    
    df = load_parquet_data()
    
    if df is None or df.empty:
        st.error("Unable to load data. Please check the data source.")
        st.stop()
    
    required_columns = ["delta_valence", "delta_arousal", "subjective_valence", "subjective_arousal", 
                        "objective_valence", "objective_arousal", "fused_valence", "fused_arousal"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()
    
    avg_delta_v = df["delta_valence"].mean()
    avg_delta_a = df["delta_arousal"].mean()
    
    c1, c2 = st.columns(2)
    c1.metric("Average Δ Valence", f"{avg_delta_v:.3f}" if not pd.isna(avg_delta_v) else "N/A")
    c2.metric("Average Δ Arousal", f"{avg_delta_a:.3f}" if not pd.isna(avg_delta_a) else "N/A")
        
    panel_header("Affective Variance Analysis", "Dual View")
    
    st.markdown("#### Topography (Density Map)")
    col1, col2 = st.columns([3, 1])
    with col1:
        data_type = st.radio("Select Data Layer", ["Subjective", "Objective", "Target (Fused)"], horizontal=True, key="af_data_type")
    with col2:
        st.write("")
        st.write("")
        show_target_vectors = st.toggle("Show Target Vectors", value=False, key="af_show_vectors")
    
    if data_type == "Subjective":
        x_data = df['subjective_valence']
        y_data = df['subjective_arousal']
        marker_color = "#4287C6"
    elif data_type == "Objective":
        x_data = df['objective_valence']
        y_data = df['objective_arousal']
        marker_color = "#1C5B99"
    else:
        x_data = df['fused_valence']
        y_data = df['fused_arousal']
        marker_color = "#FFFFFF"
        
    fig_density = go.Figure()
    fig_density.add_trace(go.Histogram2dContour(
        x=x_data, y=y_data,
        colorscale="Viridis",
        reversescale=False,
        showscale=False,
        ncontours=15,
        opacity=0.7,
        contours=dict(showlabels=False)
    ))
    fig_density.add_trace(go.Scatter(
        x=x_data, y=y_data,
        mode='markers',
        marker=dict(color=marker_color, size=6, opacity=0.8, line=dict(color="rgba(0,0,0,0.5)", width=1)),
        name=data_type,
        hovertemplate="Valence: %{x:.2f}<br>Arousal: %{y:.2f}<extra></extra>"
    ))
    if show_target_vectors and data_type != "Target (Fused)":
        if data_type == "Subjective":
            active_v, active_a = 'subjective_valence', 'subjective_arousal'
        else:
            active_v, active_a = 'objective_valence', 'objective_arousal'
            
        for _, row in df.iterrows():
            if pd.notna(row[active_v]) and pd.notna(row[active_a]) and pd.notna(row['fused_valence']) and pd.notna(row['fused_arousal']):
                fig_density.add_annotation(
                    x=row['fused_valence'], y=row['fused_arousal'],
                    ax=row[active_v], ay=row[active_a],
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowcolor='rgba(255, 255, 255, 0.15)',
                    arrowsize=1,
                    arrowwidth=1,
                    arrowhead=2
                )

    style_figure(fig_density, f"{data_type} Density Field", height=500)
    fig_density.update_xaxes(zeroline=True, zerolinecolor="#0F2D53", zerolinewidth=2, range=[-1.1, 1.1], title="Valence")
    fig_density.update_yaxes(zeroline=True, zerolinecolor="#0F2D53", zerolinewidth=2, range=[-1.1, 1.1], title="Arousal")
    st.plotly_chart(fig_density, use_container_width=True)
