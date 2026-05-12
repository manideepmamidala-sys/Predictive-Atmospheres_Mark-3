import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Optional
from src.config import get_config
from frontend.ui.data_utils import load_parquet_data
from src.services.container import ServiceContainer
from frontend.ui.theme import render_hero, style_figure, panel_header
from frontend.ui.state_utils import get_current_features_from_state


def _percentile_rank(values: np.ndarray, value: float) -> float:
    if len(values) == 0:
        return 0.0
    return float((np.sum(values <= value) / len(values)) * 100.0)


def render_page(services: Optional[ServiceContainer] = None):
    render_hero(
        "Design Benchmark",
        "Benchmark current configuration against dataset distributions across all spatial features.",
        kicker="Comparative Analysis",
        compact=True,
    )

    config = get_config()
    df = load_parquet_data()

    df["NeuroScore"] = (df["fused_valence"] + 1.0) / 2.0

    if "Length_m" in df.columns and "Width_m" in df.columns and "Height_m" in df.columns:
        df["Volume_m3"] = df["Length_m"] * df["Width_m"] * df["Height_m"]
    else:
        df["Volume_m3"] = 0.0

    if "L" not in st.session_state:
        st.session_state["L"] = config.room.default_length
    if "W" not in st.session_state:
        st.session_state["W"] = config.room.default_width
    if "H" not in st.session_state:
        st.session_state["H"] = config.room.default_height

    current = {
        "Length_m": float(st.session_state["L"]),
        "Width_m": float(st.session_state["W"]),
        "Height_m": float(st.session_state["H"]),
    }
    current["Volume_m3"] = current["Length_m"] * current["Width_m"] * current["Height_m"]

    current_score = None
    if services is not None and "spatial_model" in st.session_state and st.session_state.get("trained", False):
        full_features = get_current_features_from_state(config)
        feature_names = st.session_state.get('feature_names', [])
        if feature_names and len(feature_names) > 3:
            prediction = services.prediction_service.predict_full(full_features)
        else:
            prediction = services.prediction_service.predict(
                current["Length_m"], current["Width_m"], current["Height_m"]
            )
        current_score = (prediction.valence + 1.0) / 2.0
        
        if 'Daylight Factor (%)' in full_features:
            current['Daylight_Factor_pct'] = full_features['Daylight Factor (%)']
        if 'Illuminance (lux)' in full_features:
            current['Illuminance_lux'] = full_features['Illuminance (lux)']
        if 'Walkable Floor Area (sq.meter)' in full_features:
            current['Walkable_Floor_Area_m2'] = full_features['Walkable Floor Area (sq.meter)']

    key_dims = []
    for col in ["Length_m", "Width_m", "Height_m", "Volume_m3"]:
        if col in df.columns and col in current:
            key_dims.append(col)

    if key_dims:
        cols = st.columns(len(key_dims))
        for idx, dim in enumerate(key_dims):
            short_name = dim.replace('_m3', ' m³').replace('_m', ' m')
            cols[idx].metric(f"{short_name} Percentile", f"{_percentile_rank(df[dim].values, current.get(dim, 0.0)):.1f}%")

    if current_score is not None:
        st.caption(f"Current predicted Neuro-Score: {current_score:.2f}")

    panel_header("Benchmark Views", "Comparative Charts")
    left, right = st.columns(2)

    with left:
        numeric_cols = [c for c in df.columns
                        if c not in ('NeuroScore', 'Volume_m3', 'Subject_ID', 'Room_ID', 'EEG_Filename', 'experiment_id')
                        and df[c].dtype.kind in 'biufc'
                        and df[c].nunique() > 1
                        and not c.startswith('Day_or_Night_')
                        and not c.startswith('Type_of_Space_')
                        and not c.startswith('gender_')]

        if len(numeric_cols) > 8:
            corr = df[numeric_cols + ['NeuroScore']].corr()['NeuroScore'].drop('NeuroScore').abs()
            numeric_cols = corr.nlargest(8).index.tolist()

        dims = numeric_cols + ["Volume_m3"] if "Volume_m3" in df.columns and df["Volume_m3"].sum() > 0 else numeric_cols
        dims = [d for d in dims if d in df.columns]

        med = df[dims].median()
        q3 = df[dims].quantile(0.75)

        cur_vals = []
        for d in dims:
            cur_vals.append(current.get(d, med[d]))
        cur = np.array(cur_vals, dtype=float)

        denom = np.maximum(q3.values, 1e-8)
        cur_norm = np.clip(cur / denom, 0, 1.25)
        med_norm = np.clip(med.values / denom, 0, 1.25)
        q3_norm = np.ones_like(cur_norm)

        short_dims = [d.replace('_m2', ' m²').replace('_m3', ' m³').replace('_m', ' m').replace('_pct', ' %').replace('_lux', ' lux').replace('_K', ' K')[:20] for d in dims]
        theta = short_dims + [short_dims[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=list(cur_norm) + [cur_norm[0]],
                theta=theta,
                fill="toself",
                name="Current Design",
                line=dict(color="#2FD4C8", width=2),
                fillcolor="rgba(47,212,200,0.25)",
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=list(med_norm) + [med_norm[0]],
                theta=theta,
                fill="toself",
                name="Dataset Median",
                line=dict(color="#8B7CFF", width=2),
                fillcolor="rgba(139,124,255,0.20)",
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=list(q3_norm) + [q3_norm[0]],
                theta=theta,
                mode="lines",
                name="Q3 Baseline",
                line=dict(color="#FF6B8A", width=2, dash="dash"),
            )
        )
        style_figure(fig_radar, "Design Position vs Dataset Baselines", height=430)
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 1.25], gridcolor="rgba(15,45,83,0.5)", linecolor="rgba(15,45,83,0.8)"),
                bgcolor="rgba(0,0,0,0)",
            )
        )
        st.plotly_chart(fig_radar, width="stretch")

    with right:
        if df["Volume_m3"].sum() > 0:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(
                go.Scatter(
                    x=df["Volume_m3"],
                    y=df["NeuroScore"],
                    mode="markers",
                    marker=dict(
                        size=9,
                        color=df.get("Height_m", df["NeuroScore"]),
                        colorscale="Viridis",
                        opacity=0.68,
                        colorbar=dict(title="Height" if "Height_m" in df.columns else "Score"),
                    ),
                    name="Dataset",
                    hovertemplate="Volume: %{x:.2f}<br>Neuro-Score: %{y:.2f}<extra></extra>",
                )
            )

            if current_score is not None:
                fig_scatter.add_trace(
                    go.Scatter(
                        x=[current["Volume_m3"]],
                        y=[current_score],
                        mode="markers",
                        marker=dict(size=14, color="#E8ECF7", symbol="diamond", line=dict(color="#0B0F18", width=2)),
                        name="Current Design",
                        hovertemplate="Current Volume: %{x:.2f}<br>Current Score: %{y:.2f}<extra></extra>",
                    )
                )

            style_figure(fig_scatter, "Volume vs Neuro-Score Benchmark", height=430)
            fig_scatter.update_layout(xaxis_title="Volume (m³)", yaxis_title="Neuro-Score")
            st.plotly_chart(fig_scatter, width="stretch")
        else:
            st.info("Volume data not available for benchmark visualization.")
