import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Optional
from frontend.ui.data_utils import load_parquet_data
from src.services.container import ServiceContainer
from frontend.ui.theme import render_hero, style_figure, panel_header
from frontend.ui.state_utils import get_current_features_from_state
from src.config import get_config


def render_page(services: Optional[ServiceContainer] = None):
    render_hero(
        "Emotion Landscape",
        "Global view of the learned affective space and how spatial configurations populate valence-arousal territory across all features.",
        kicker="Affective Analysis",
        compact=True,
    )

    df = load_parquet_data()
    
    df["Valence"] = df["fused_valence"]
    df["Arousal"] = df["fused_arousal"]
    df["NeuroScore"] = (df["Valence"] + 1.0) / 2.0

    if "Length_m" in df.columns and "Width_m" in df.columns and "Height_m" in df.columns:
        df["Volume_m3"] = df["Length_m"] * df["Width_m"] * df["Height_m"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", len(df))
    c2.metric("Mean Neuro-Score", f"{df['NeuroScore'].mean():.2f}")
    c3.metric("Mean Valence", f"{df['Valence'].mean():.2f}")
    c4.metric("Mean Arousal", f"{df['Arousal'].mean():.2f}")

    panel_header("Spatial Distribution", "Dataset")

    numeric_features = [c for c in df.columns
                        if c not in ('Valence', 'Arousal', 'NeuroScore', 'Volume_m3', 'Subject_ID', 'Room_ID', 'EEG_Filename', 'experiment_id', 'fused_valence', 'fused_arousal', 'objective_valence', 'objective_arousal', 'subjective_valence', 'subjective_arousal', 'delta_valence', 'delta_arousal', 'euclidean_distance', 'alpha_used')
                        and df[c].dtype.kind in 'biufc'
                        and df[c].nunique() > 1
                        and not c.startswith('Day_or_Night_')
                        and not c.startswith('Type_of_Space_')
                        and not c.startswith('gender_')]

    default_axes = []
    for preferred in ["Length_m", "Width_m", "Height_m"]:
        if preferred in numeric_features:
            default_axes.append(preferred)
    while len(default_axes) < 3 and len(numeric_features) > len(default_axes):
        for f in numeric_features:
            if f not in default_axes:
                default_axes.append(f)
                break

    col_ax1, col_ax2, col_ax3 = st.columns(3)
    with col_ax1:
        x_axis = st.selectbox("X Axis", numeric_features, index=numeric_features.index(default_axes[0]) if default_axes and default_axes[0] in numeric_features else 0, key="el_x_axis")
    with col_ax2:
        y_axis = st.selectbox("Y Axis", numeric_features, index=numeric_features.index(default_axes[1]) if len(default_axes) > 1 and default_axes[1] in numeric_features else min(1, len(numeric_features)-1), key="el_y_axis")
    with col_ax3:
        z_axis = st.selectbox("Z Axis", numeric_features, index=numeric_features.index(default_axes[2]) if len(default_axes) > 2 and default_axes[2] in numeric_features else min(2, len(numeric_features)-1), key="el_z_axis")

    fig_space = go.Figure()
    fig_space.add_trace(
        go.Scatter3d(
            x=df[x_axis],
            y=df[y_axis],
            z=df[z_axis],
            mode="markers",
            marker=dict(
                size=6,
                color=df["NeuroScore"],
                colorscale=[[0, "#FF6B8A"], [0.5, "#8B7CFF"], [1, "#2FD4C8"]],
                cmin=0,
                cmax=1,
                colorbar=dict(title="Neuro-Score"),
                opacity=0.85,
            ),
            customdata=np.stack([df["Valence"], df["Arousal"]], axis=1),
            hovertemplate=(
                f"{x_axis}: %{{x:.2f}}<br>{y_axis}: %{{y:.2f}}<br>{z_axis}: %{{z:.2f}}"
                "<br>Valence: %{customdata[0]:.2f}<br>Arousal: %{customdata[1]:.2f}<extra></extra>"
            ),
            name="Dataset Rooms",
        )
    )

    if services is not None and "L" in st.session_state and "W" in st.session_state and "H" in st.session_state:
        config = get_config()
        full_features = get_current_features_from_state(config)
        
        design_point = {}
        for axis in (x_axis, y_axis, z_axis):
            if axis == 'Length_m': design_point[axis] = full_features.get('Length (meter)')
            elif axis == 'Width_m': design_point[axis] = full_features.get('Width (meter)')
            elif axis == 'Height_m': design_point[axis] = full_features.get('Height (meter)')
            elif axis == 'Daylight_Factor_pct': design_point[axis] = full_features.get('Daylight Factor (%)')
            elif axis == 'Illuminance_lux': design_point[axis] = full_features.get('Illuminance (lux)')
            elif axis == 'Walkable_Floor_Area_m2': design_point[axis] = full_features.get('Walkable Floor Area (sq.meter)')
            else: design_point[axis] = None
            
        if all(v is not None for v in design_point.values()):
            fig_space.add_trace(
                go.Scatter3d(
                    x=[design_point[x_axis]],
                    y=[design_point[y_axis]],
                    z=[design_point[z_axis]],
                    mode="markers",
                    marker=dict(size=10, color="#E8ECF7", symbol="diamond", line=dict(color="#0B0F18", width=2)),
                    name="Current Design",
                    hovertemplate=f"Current design<br>{x_axis}: %{{x:.2f}}<br>{y_axis}: %{{y:.2f}}<br>{z_axis}: %{{z:.2f}}<extra></extra>",
                )
            )

    style_figure(fig_space, "Spatial Configuration Distribution", height=520)
    fig_space.update_layout(
        scene=dict(
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            zaxis_title=z_axis,
            bgcolor="rgba(0,0,0,0)",
        )
    )
    st.plotly_chart(fig_space, width="stretch")

    panel_header("Affective Density + Volume Benchmarks", "Comparative Views")
    left, right = st.columns(2)

    with left:
        fig_va = go.Figure()
        fig_va.add_trace(
            go.Histogram2dContour(
                x=df["Valence"],
                y=df["Arousal"],
                colorscale="Viridis",
                ncontours=12,
                reversescale=False,
                showscale=True,
                colorbar=dict(title="Density"),
                contours=dict(showlabels=False),
                opacity=0.82,
                name="Density",
            )
        )
        fig_va.add_trace(
            go.Scatter(
                x=df["Valence"],
                y=df["Arousal"],
                mode="markers",
                marker=dict(size=4, color="rgba(232,236,247,0.45)"),
                hovertemplate="Valence: %{x:.2f}<br>Arousal: %{y:.2f}<extra></extra>",
                name="Samples",
            )
        )
        style_figure(fig_va, "Valence-Arousal Density Field", height=380)
        fig_va.update_layout(xaxis_title="Valence", yaxis_title="Arousal")
        st.plotly_chart(fig_va, width="stretch")

    with right:
        if df["Volume_m3"].sum() > 0:
            df_bin = df.copy()
            bins = pd.qcut(df_bin["Volume_m3"], q=4, duplicates="drop")
            summary = df_bin.groupby(bins, observed=True)["NeuroScore"].mean().reset_index()
            summary["VolumeBin"] = summary.iloc[:, 0].astype(str)

            fig_vol = go.Figure(
                go.Bar(
                    x=summary["VolumeBin"],
                    y=summary["NeuroScore"],
                    marker=dict(color="#8B7CFF"),
                    text=[f"{v:.2f}" for v in summary["NeuroScore"]],
                    textposition="outside",
                    hovertemplate="Volume Bin: %{x}<br>Avg Neuro-Score: %{y:.3f}<extra></extra>",
                )
            )
            style_figure(fig_vol, "Neuro-Score by Volume Quartile", height=380)
            fig_vol.update_layout(xaxis_title="Volume Quartile", yaxis_title="Average Neuro-Score")
            st.plotly_chart(fig_vol, width="stretch")
        else:
            st.info("Volume data not available for quartile analysis.")
