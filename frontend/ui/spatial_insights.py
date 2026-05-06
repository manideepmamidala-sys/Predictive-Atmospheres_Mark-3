import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.data.data_loader import load_data
from frontend.ui.base_visualization import BaseVisualization
from frontend.ui.theme import style_figure, panel_header

class SpatialInsightsVis(BaseVisualization):
    def __init__(self):
        super().__init__(
            title="Spatial-Neuro Correlation Analysis",
            description="Understand how architectural parameters map onto predicted emotional quality and neuro-score outcomes across all features."
        )

    def load_data(self):
        # Prefer full-feature training data from session state
        if hasattr(st, 'session_state') and 'train_X' in st.session_state:
            self.X = st.session_state.train_X
            self.y_va_data = st.session_state.train_y_va
        else:
            self.X, self.y_va_data, _ = load_data()
        self.feature_names = st.session_state.get('feature_names', [])

    def process_data(self):
        if self.feature_names and len(self.feature_names) == self.X.shape[1]:
            self.df_spatial = pd.DataFrame(self.X, columns=self.feature_names)
        elif self.X.shape[1] == 3:
            self.df_spatial = pd.DataFrame(self.X, columns=['Length (meter)', 'Width (meter)', 'Height (meter)'])
        else:
            self.df_spatial = pd.DataFrame(self.X, columns=[f"Feature_{i}" for i in range(self.X.shape[1])])

        y_stress = []
        for va in self.y_va_data:
            v = va[0]
            stress_val = 1.0 - ((v + 1.0) / 2.0)
            y_stress.append(stress_val)

        self.df_spatial['NeuroScore'] = 1.0 - np.array(y_stress)

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

        short_name = x_col.replace(' (meter)', '').replace(' (sq.meter)', '').replace(' (%)', '')
        style_figure(fig, f"{short_name} vs Neuro-Score", height=320)
        fig.update_layout(xaxis_title=x_col, yaxis_title='Neuro Score')
        return fig

    def build_charts(self):
        # Filter out categorical one-hot columns for numeric correlation analysis
        numeric_cols = [c for c in self.df_spatial.columns
                        if c != 'NeuroScore'
                        and not c.startswith('Day or Night_')
                        and self.df_spatial[c].dtype.kind in 'biufc'
                        and self.df_spatial[c].nunique() > 1]

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

        # Dynamic colors
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

        # For many features, use a selector
        if len(numeric_cols) > 6:
            selected_features = st.multiselect(
                "Select features to visualize",
                numeric_cols,
                default=numeric_cols[:6],
                key="spatial_feature_select"
            )
        else:
            selected_features = numeric_cols

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
