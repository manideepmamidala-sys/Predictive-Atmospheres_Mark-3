import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from frontend.ui.base_visualization import BaseVisualization
from frontend.ui.theme import style_figure, panel_header
from frontend.ui.data_utils import load_parquet_data

class SpatialInsightsVis(BaseVisualization):
    def __init__(self):
        super().__init__(
            title="Spatial-Neuro Correlation Analysis",
            description="Understand how architectural parameters map onto predicted emotional quality and neuro-score outcomes across all features."
        )

    def load_data(self):
        self.df_spatial = load_parquet_data()

    def process_data(self):
        self.df_spatial['NeuroScore'] = (self.df_spatial['fused_valence'] + 1.0) / 2.0

    def _plot_reg(self, x_col, y_col='NeuroScore'):
        x_vals = self.df_spatial[x_col]
        y_vals = self.df_spatial[y_col]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                name='Observed',
                marker=dict(
                    size=11,
                    color=y_vals,
                    colorscale=[[0, '#FF6B8A'], [0.5, '#8B7CFF'], [1, '#2FD4C8']],
                    cmin=float(self.df_spatial[y_col].min()),
                    cmax=float(self.df_spatial[y_col].max()),
                    line=dict(color='rgba(9,11,18,0.8)', width=1),
                ),
                hovertemplate=f"{x_col}: %{{x:.2f}}<br>{y_col}: %{{y:.3f}}<extra></extra>",
            )
        )
        if len(self.df_spatial) > 1:
            z = np.polyfit(x_vals, y_vals, 1)
            p = np.poly1d(z)
            x_range = np.linspace(float(x_vals.min()), float(x_vals.max()), 100)
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=p(x_range),
                    mode='lines',
                    name='Trend',
                    line=dict(color='#E8ECF7', width=2, dash='dash'),
                )
            )

        short_name = x_col.replace('_m2', ' m²').replace('_m', ' m').replace('_pct', ' %').replace('_lux', ' lux').replace('_K', ' K')
        style_figure(fig, f"{short_name} vs Neuro-Score", height=320)
        fig.update_layout(xaxis_title=short_name, yaxis_title='Neuro Score')
        return fig

    def build_charts(self):
        # 12 Independent spatial features
        numeric_cols = [
            "Length_m", "Width_m", "Height_m", "Num_Doors", "Door_Area_m2", 
            "Num_Windows", "Window_Area_m2", "Daylight_Factor_pct", "Illuminance_lux", 
            "CCT_K", "Walkable_Floor_Area_m2"
        ]
        numeric_cols = [c for c in numeric_cols if c in self.df_spatial.columns]

        analysis_df = self.df_spatial[numeric_cols + ['NeuroScore']].copy()

        panel_header("Correlation Matrix", "Structure")
        corr = analysis_df.corr()

        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.columns,
            colorscale=[[0, '#FF6B8A'], [0.5, '#171D30'], [1, '#2FD4C8']],
            zmin=-1,
            zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            hovertemplate="%{x} vs %{y}<br>r=%{z:.3f}<extra></extra>",
        ))
        style_figure(fig_corr, "Feature Correlations", height=max(430, len(numeric_cols) * 25))
        fig_corr.update_layout(width=None)
        st.plotly_chart(fig_corr, width='stretch')

        panel_header("Feature Influence Ranking", "Importance")
        target_corr = corr['NeuroScore'].drop(labels=['NeuroScore'])
        impact = target_corr.abs().sort_values(ascending=False)

        n_features = len(impact)
        colors = ['#2FD4C8' if i < n_features // 3
                  else '#8B7CFF' if i < 2 * n_features // 3
                  else '#FF6B8A'
                  for i in range(n_features)]

        fig_rank = go.Figure(
            go.Bar(
                x=impact.values,
                y=impact.index,
                orientation='h',
                marker=dict(color=colors[::-1]),
                text=[f"{v:.2f}" for v in impact.values],
                textposition='outside',
            )
        )
        style_figure(fig_rank, "Absolute Correlation with Neuro-Score", height=max(280, n_features * 28))
        fig_rank.update_layout(xaxis_title='|r|', yaxis_title='Feature')
        st.plotly_chart(fig_rank, width='stretch')

        panel_header("Feature Analysis", "Dimension-wise")

        selected_features = st.multiselect(
            "Select features to visualize",
            numeric_cols,
            default=numeric_cols[:6],
            key="spatial_feature_select"
        )

        if selected_features:
            n_cols = min(3, len(selected_features))
            for row_start in range(0, len(selected_features), n_cols):
                row_features = selected_features[row_start:row_start + n_cols]
                cols = st.columns(n_cols)
                for idx, feat in enumerate(row_features):
                    with cols[idx]:
                        st.plotly_chart(self._plot_reg(feat), width='stretch')

def render_page():
    vis = SpatialInsightsVis()
    vis.render()
