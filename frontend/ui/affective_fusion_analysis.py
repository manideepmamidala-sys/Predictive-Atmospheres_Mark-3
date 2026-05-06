"""
Affective Fusion Analysis Page
================================
Visualises the multimodal fusion between objective (EEG/ECG) and
subjective (self-reported) affective scores.

For each subject/room pair the page plots:
  A  – Subjective score (self-reported V/A)
  B  – Objective score (FAA valence, RMSSD arousal)
  C  – Fused ground-truth target (alpha-weighted blend)

The error/variance line between A and B is drawn, and the fused target
C is placed along that vector.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional

from frontend.ui.theme import render_hero, style_figure, panel_header
from src.config import get_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_fusion_data() -> Optional[pd.DataFrame]:
    """Load the persisted fusion analysis CSV."""
    config = get_config()
    csv_path = os.path.join(config.paths.data_dir, 'processed', 'fusion_analysis.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None


def _build_circumplex_scatter(df: pd.DataFrame, selected_idx: Optional[int] = None) -> go.Figure:
    """Build a 2-D Circumplex scatter showing Subj (A), Obj (B), Fused (C)."""
    fig = go.Figure()

    # Background quadrant shading
    for qx, qy, color, label in [
        (0.5, 0.5, 'rgba(76,175,80,0.08)', 'Happy / Excited'),
        (-0.5, 0.5, 'rgba(244,67,54,0.08)', 'Angry / Tense'),
        (-0.5, -0.5, 'rgba(33,150,243,0.08)', 'Sad / Bored'),
        (0.5, -0.5, 'rgba(156,39,176,0.08)', 'Calm / Relaxed'),
    ]:
        fig.add_shape(
            type='rect',
            x0=0 if qx > 0 else -1.1, x1=1.1 if qx > 0 else 0,
            y0=0 if qy > 0 else -1.1, y1=1.1 if qy > 0 else 0,
            fillcolor=color, line_width=0, layer='below',
        )
        fig.add_annotation(
            x=qx, y=qy, text=label, showarrow=False,
            font=dict(size=10, color='rgba(255,255,255,0.4)'),
        )

    has_subjective = df['subjective_valence'].notna().any()

    # Plot all data points
    if has_subjective:
        # A – Subjective (blue circles)
        fig.add_trace(go.Scatter(
            x=df['subjective_valence'], y=df['subjective_arousal'],
            mode='markers', name='Subjective (A)',
            marker=dict(size=7, color='#42A5F5', opacity=0.6, symbol='circle'),
            text=df['subject_id'] + ' / ' + df['room_id'].astype(str),
            hovertemplate='<b>Subjective</b><br>V=%{x:.3f} A=%{y:.3f}<br>%{text}<extra></extra>',
        ))

    # B – Objective (red diamonds)
    fig.add_trace(go.Scatter(
        x=df['objective_valence'], y=df['objective_arousal'],
        mode='markers', name='Objective (B)',
        marker=dict(size=7, color='#EF5350', opacity=0.6, symbol='diamond'),
        text=df['subject_id'] + ' / ' + df['room_id'].astype(str),
        hovertemplate='<b>Objective (EEG/ECG)</b><br>V=%{x:.3f} A=%{y:.3f}<br>%{text}<extra></extra>',
    ))

    # C – Fused (green stars)
    fig.add_trace(go.Scatter(
        x=df['fused_valence'], y=df['fused_arousal'],
        mode='markers', name='Fused Target (C)',
        marker=dict(size=10, color='#66BB6A', opacity=0.8, symbol='star'),
        text=df['subject_id'] + ' / ' + df['room_id'].astype(str),
        hovertemplate='<b>Fused Target</b><br>V=%{x:.3f} A=%{y:.3f}<br>%{text}<extra></extra>',
    ))

    # Draw variance lines for selected row or all rows
    if selected_idx is not None and has_subjective:
        row = df.iloc[selected_idx]
        if pd.notna(row['subjective_valence']):
            # Line from A to B (error vector)
            fig.add_trace(go.Scatter(
                x=[row['subjective_valence'], row['objective_valence']],
                y=[row['subjective_arousal'], row['objective_arousal']],
                mode='lines', name='Variance Vector',
                line=dict(color='#FF9800', width=2, dash='dash'),
                showlegend=True,
            ))
            # Highlight fused point
            fig.add_trace(go.Scatter(
                x=[row['fused_valence']], y=[row['fused_arousal']],
                mode='markers', name='Selected Fused',
                marker=dict(size=16, color='#FFEB3B', symbol='star', line=dict(width=2, color='#333')),
                showlegend=True,
            ))
    elif has_subjective and len(df) <= 50:
        # Draw all variance lines if dataset is small
        for _, row in df.iterrows():
            if pd.notna(row.get('subjective_valence')):
                fig.add_trace(go.Scatter(
                    x=[row['subjective_valence'], row['objective_valence']],
                    y=[row['subjective_arousal'], row['objective_arousal']],
                    mode='lines', line=dict(color='rgba(255,152,0,0.25)', width=1),
                    showlegend=False, hoverinfo='skip',
                ))

    # Axes
    fig.update_layout(
        xaxis=dict(title='Valence', range=[-1.1, 1.1], zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
        yaxis=dict(title='Arousal', range=[-1.1, 1.1], zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
        height=600, template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    style_figure(fig)
    return fig


# ---------------------------------------------------------------------------
# Page entry point
# ---------------------------------------------------------------------------

def render_page(**kwargs):
    """Render the Affective Fusion Analysis page."""
    render_hero(
        "Affective Fusion Analysis",
        "Multimodal fusion of objective (EEG/ECG) and subjective (self-reported) "
        "scores into a single ground-truth target for model training.",
        kicker="Data Pipeline Transparency",
        compact=True,
    )

    config = get_config()
    fusion_df = _load_fusion_data()

    if fusion_df is None or fusion_df.empty:
        st.warning(
            "No fusion analysis data available. "
            "Run model training first to generate the fusion_analysis.csv."
        )
        return

    # ---- Summary Metrics ----
    panel_header("Fusion Summary", "Overview")
    alpha = config.fusion.alpha

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Samples", len(fusion_df))
    col2.metric("Alpha (Objective Weight)", f"{alpha:.2f}")

    has_subj = fusion_df['subjective_valence'].notna().sum()
    col3.metric("With Subjective", int(has_subj))

    if 'euclidean_distance' in fusion_df.columns:
        valid_dist = fusion_df['euclidean_distance'].dropna()
        col4.metric("Mean Euclidean Δ", f"{valid_dist.mean():.4f}" if len(valid_dist) > 0 else "N/A")

    st.markdown("---")

    # ---- Circumplex Plot ----
    panel_header("Circumplex Scatter", "Visualization")

    # Subject/room selector
    labels = (fusion_df['subject_id'].astype(str) + ' / Room ' + fusion_df['room_id'].astype(str)).tolist()
    selected = st.selectbox("Highlight a specific subject/room pair", ["All"] + labels)
    sel_idx = labels.index(selected) if selected != "All" else None

    fig = _build_circumplex_scatter(fusion_df, selected_idx=sel_idx)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"**Legend:** Blue circles = Self-reported (A), Red diamonds = EEG/ECG objective (B), "
        f"Green stars = Fused target (C). α = {alpha:.2f}. "
        f"Fusion: C = α·B + (1-α)·A"
    )

    st.markdown("---")

    # ---- Delta Table ----
    panel_header("Variance Table", "Numeric Deltas")

    display_cols = [
        'subject_id', 'room_id', 'experiment',
        'objective_valence', 'objective_arousal',
        'subjective_valence', 'subjective_arousal',
        'fused_valence', 'fused_arousal',
        'delta_valence', 'delta_arousal', 'euclidean_distance',
    ]
    available = [c for c in display_cols if c in fusion_df.columns]

    styled_df = fusion_df[available].copy()
    # Round numeric columns for readability
    for c in styled_df.columns:
        if styled_df[c].dtype in ('float64', 'float32'):
            styled_df[c] = styled_df[c].round(4)

    st.dataframe(styled_df, use_container_width=True, height=400)

    # ---- Distribution ----
    panel_header("Delta Distribution", "Histogram")
    if 'euclidean_distance' in fusion_df.columns:
        valid_dist = fusion_df['euclidean_distance'].dropna()
        if len(valid_dist) > 0:
            hist_fig = go.Figure()
            hist_fig.add_trace(go.Histogram(
                x=valid_dist, nbinsx=20,
                marker_color='#66BB6A', opacity=0.8,
                name='Euclidean Distance',
            ))
            hist_fig.update_layout(
                xaxis_title='Euclidean Distance (Obj vs Subj)',
                yaxis_title='Count',
                template='plotly_dark', height=300,
                margin=dict(l=40, r=40, t=20, b=40),
            )
            style_figure(hist_fig)
            st.plotly_chart(hist_fig, use_container_width=True)
            st.caption(
                "Distribution of Euclidean distances between objective and subjective "
                "coordinates. Larger distances indicate higher disagreement between "
                "biometric signals and self-report."
            )
