import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from typing import Optional
from src.config import get_config
from src.data.data_loader import load_data
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
    # Prefer full-feature training data from session state
    if hasattr(st, 'session_state') and 'train_X' in st.session_state:
        X = st.session_state.train_X
        y_va = st.session_state.train_y_va
    else:
        X, y_va, _ = load_data()
    feature_names = st.session_state.get('feature_names', [])

    if feature_names and len(feature_names) == X.shape[1]:
        df = pd.DataFrame(X, columns=feature_names)
    elif X.shape[1] == 3:
        df = pd.DataFrame(X, columns=["Length (meter)", "Width (meter)", "Height (meter)"])
    else:
        df = pd.DataFrame(X, columns=[f"Feature_{i}" for i in range(X.shape[1])])

    df["NeuroScore"] = (y_va[:, 0] + 1.0) / 2.0

    # Compute volume
    if "Length (meter)" in df.columns and "Width (meter)" in df.columns and "Height (meter)" in df.columns:
        df["Volume"] = df["Length (meter)"] * df["Width (meter)"] * df["Height (meter)"]
    elif "Volume (cubic.meter)" in df.columns:
        df["Volume"] = df["Volume (cubic.meter)"]
    else:
        df["Volume"] = 0.0

    if "L" not in st.session_state:
        st.session_state["L"] = config.room.default_length
    if "W" not in st.session_state:
        st.session_state["W"] = config.room.default_width
    if "H" not in st.session_state:
        st.session_state["H"] = config.room.default_height

    current = {
        "Length (meter)": float(st.session_state["L"]),
        "Width (meter)": float(st.session_state["W"]),
        "Height (meter)": float(st.session_state["H"]),
    }
    current["Volume"] = current["Length (meter)"] * current["Width (meter)"] * current["Height (meter)"]

    current_score = None
    if services is not None and "spatial_model" in st.session_state and st.session_state.get("trained", False):
        config = get_config()
        full_features = get_current_features_from_state(config)
        feature_names = st.session_state.get('feature_names', [])
        if feature_names and len(feature_names) > 3:
            prediction = services.prediction_service.predict_full(full_features)
        else:
            prediction = services.prediction_service.predict(
                current["Length (meter)"], current["Width (meter)"], current["Height (meter)"]
            )
        current_score = (prediction.valence + 1.0) / 2.0
        # merge full features for radar chart
        current.update({k: v for k, v in full_features.items() if k not in current})

    # Percentile metrics for key features
    key_dims = []
    for col in ["Length (meter)", "Width (meter)", "Height (meter)", "Volume"]:
        if col in df.columns and col in current:
            key_dims.append(col)

    if key_dims:
        cols = st.columns(len(key_dims))
        for idx, dim in enumerate(key_dims):
            short_name = dim.replace(' (meter)', '').replace(' (cubic.meter)', '').replace(' (sq.meter)', '')
            cols[idx].metric(f"{short_name} Percentile", f"{_percentile_rank(df[dim].values, current.get(dim, 0.0)):.1f}%")

    if current_score is not None:
        st.caption(f"Current predicted Neuro-Score: {current_score:.2f}")

    panel_header("Benchmark Views", "Comparative Charts")
    left, right = st.columns(2)

    with left:
        # Radar chart with all numeric features from the dataset
        numeric_cols = [c for c in df.columns
                        if c not in ('NeuroScore', 'Volume')
                        and df[c].dtype.kind in 'biufc'
                        and df[c].nunique() > 1
                        and not c.startswith('Day or Night_')]

        # If too many features, select top correlated ones
        if len(numeric_cols) > 8:
            corr = df[numeric_cols + ['NeuroScore']].corr()['NeuroScore'].drop('NeuroScore').abs()
            numeric_cols = corr.nlargest(8).index.tolist()

        dims = numeric_cols + ["Volume"] if "Volume" in df.columns and df["Volume"].sum() > 0 else numeric_cols
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

        short_dims = [d.replace(' (meter)', '').replace(' (sq.meter)', ' m²').replace(' (cubic.meter)', ' m³').replace(' (%)', '%')[:20] for d in dims]
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
                radialaxis=dict(range=[0, 1.25], gridcolor="rgba(167,177,203,0.20)", linecolor="rgba(167,177,203,0.3)"),
                bgcolor="rgba(17,22,37,0.70)",
            )
        )
        st.plotly_chart(fig_radar, width="stretch")

    with right:
        if df["Volume"].sum() > 0:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(
                go.Scatter(
                    x=df["Volume"],
                    y=df["NeuroScore"],
                    mode="markers",
                    marker=dict(
                        size=9,
                        color=df.get("Height (meter)", df["NeuroScore"]),
                        colorscale="Viridis",
                        opacity=0.68,
                        colorbar=dict(title="Height" if "Height (meter)" in df.columns else "Score"),
                    ),
                    name="Dataset",
                    hovertemplate="Volume: %{x:.2f}<br>Neuro-Score: %{y:.2f}<extra></extra>",
                )
            )

            if current_score is not None:
                fig_scatter.add_trace(
                    go.Scatter(
                        x=[current["Volume"]],
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
