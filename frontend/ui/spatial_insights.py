import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
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
        if 'fused_valence' not in self.df_spatial.columns:
            raise ValueError("Missing required column 'fused_valence' in spatial data")
        self.df_spatial['NeuroScore'] = (self.df_spatial['fused_valence'] + 1.0) / 2.0

    def build_charts(self):
        # 11 Independent spatial features
        numeric_cols = [
            "Length_m", "Width_m", "Height_m", "Num_Doors", "Door_Area_m2", 
            "Num_Windows", "Window_Area_m2", "Daylight_Factor_pct", "Illuminance_lux", 
            "CCT_K", "Walkable_Floor_Area_m2"
        ]
        numeric_cols = [c for c in numeric_cols if c in self.df_spatial.columns]

        analysis_df = self.df_spatial[numeric_cols + ['NeuroScore']].copy()

        panel_header("Room Profile", "Spatial Signatures")

        room_col = 'Room ID' if 'Room ID' in self.df_spatial.columns else 'Room_ID'
        exp_col = 'Experiment'
        
        # Task 1: Dynamically create Experiment column based on Room ID
        if room_col in self.df_spatial.columns:
            room_nums = self.df_spatial[room_col].astype(str).str.extract(r'(\d+)')[0].astype(float)
            def assign_exp(num):
                if pd.isna(num): return "Experiment 3"
                if 1 <= num <= 10: return "Experiment 1"
                if 11 <= num <= 20: return "Experiment 2"
                return "Experiment 3"
            self.df_spatial[exp_col] = room_nums.apply(assign_exp)
        
        # Task 2: UI Filtering Mechanics
        available_exps = ["Experiment 1", "Experiment 2", "Experiment 3"]
        selected_exps = st.multiselect("Filter by Experiment", options=available_exps, default=available_exps)

        mask = pd.Series(True, index=self.df_spatial.index)
        if exp_col in self.df_spatial.columns and selected_exps:
            mask &= self.df_spatial[exp_col].isin(selected_exps)
            
        df_filtered = self.df_spatial[mask].copy()

        if not df_filtered.empty:
            # Task 1: Data Truncation (NaN Injection)
            if exp_col in df_filtered.columns:
                exp1_mask = df_filtered[exp_col] == "Experiment 1"
                exp2_mask = df_filtered[exp_col] == "Experiment 2"
                
                if exp1_mask.any():
                    cols_to_nan_1 = [c for c in numeric_cols if c not in ["Length_m", "Width_m", "Height_m"]]
                    df_filtered.loc[exp1_mask, cols_to_nan_1] = np.nan
                
                if exp2_mask.any():
                    if "Walkable_Floor_Area_m2" in df_filtered.columns:
                        df_filtered.loc[exp2_mask, "Walkable_Floor_Area_m2"] = np.nan

            # Task 1: Melt the DataFrame
            id_vars = [c for c in [room_col, exp_col] if c in df_filtered.columns]
            df_melted = pd.melt(
                df_filtered,
                id_vars=id_vars,
                value_vars=[c for c in numeric_cols if c in df_filtered.columns],
                var_name="Spatial Feature",
                value_name="Actual_Value"
            )

            # Task 1: Custom Scaling
            scale_multipliers = {
                'Length_m': 3.0,
                'Width_m': 3.0,
                'Height_m': 10.0,
                'Num_Doors': 10.0,
                'Door_Area_m2': 5.0,
                'Num_Windows': 2.0,
                'Window_Area_m2': 0.8,
                'Daylight_Factor_pct': 5.0,
                'Illuminance_lux': 0.05,
                'CCT_K': 0.01,
                'Walkable_Floor_Area_m2': 1.0
            }
            
            df_melted['Scaled_Y_Axis'] = df_melted['Actual_Value'] * df_melted['Spatial Feature'].map(scale_multipliers).fillna(1.0)

            # Task 3: Plotly Execution
            color_map = {
                'Experiment 1': '#E9F3F9',
                'Experiment 2': '#65ABD3',
                'Experiment 3': '#0C58A2'
            }
            
            hover_dict = {"Scaled_Y_Axis": False, "Actual_Value": ":.2f"}
            if room_col in df_melted.columns:
                hover_dict[room_col] = True

            fig_profile = px.line(
                df_melted,
                x="Spatial Feature",
                y="Scaled_Y_Axis",
                color=exp_col if exp_col in df_melted.columns else None,
                line_group=room_col if room_col in df_melted.columns else None,
                markers=True,
                color_discrete_map=color_map,
                hover_data=hover_dict
            )

            # Task 2: Inject Background Text Annotations
            for feat in numeric_cols:
                if feat in df_filtered.columns:
                    min_val = df_filtered[feat].min()
                    max_val = df_filtered[feat].max()
                    
                    feat_melted = df_melted[df_melted['Spatial Feature'] == feat]
                    if not feat_melted.empty:
                        norm_min = feat_melted['Scaled_Y_Axis'].min()
                        norm_max = feat_melted['Scaled_Y_Axis'].max()
                        
                        if pd.notna(min_val) and pd.notna(norm_min):
                            fig_profile.add_annotation(
                                x=feat, y=norm_min,
                                text=f"{min_val:.1f}",
                                showarrow=False,
                                font=dict(size=10, color="rgba(255,255,255,0.6)"),
                                xanchor="left",
                                xshift=5,
                                yshift=-10
                            )
                        if pd.notna(max_val) and pd.notna(norm_max):
                            fig_profile.add_annotation(
                                x=feat, y=norm_max,
                                text=f"{max_val:.1f}",
                                showarrow=False,
                                font=dict(size=10, color="rgba(255,255,255,0.6)"),
                                xanchor="left",
                                xshift=5,
                                yshift=10
                            )

            style_figure(fig_profile, "Normalized Spatial Signatures by Room", height=500)
            fig_profile.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Spatial Feature"),
                yaxis=dict(showgrid=False, title="Scaled Value", visible=False)
            )
            st.plotly_chart(fig_profile, use_container_width=True)
        else:
            st.warning("No rooms match the selected filters.", icon="⚠️")

        # -------------------------------------------------------------
        # Phase 2: Categorical Spatial Thresholds
        # -------------------------------------------------------------
        panel_header("Categorical Spatial Thresholds", "Threshold Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Day vs. Night Impact")
            df_dn = self.df_spatial.copy()
            
            def assign_dn(row):
                if row.get('Day_or_Night_Day', 0) == 1: return "Day"
                if row.get('Day_or_Night_Night', 0) == 1: return "Night"
                return "Unknown"
                
            df_dn['Time_Condition'] = df_dn.apply(assign_dn, axis=1)
            df_dn = df_dn[df_dn['Time_Condition'] != "Unknown"]
            
            if not df_dn.empty:
                fig_dn = px.box(
                    df_dn, x="Time_Condition", y="NeuroScore", 
                    points="all", color="Time_Condition",
                    color_discrete_map={"Day": "#2FD4C8", "Night": "#8B7CFF"}
                )
                style_figure(fig_dn, "Objective Neuro-Score by Time of Day", height=400)
                fig_dn.update_layout(xaxis_title="Condition", yaxis_title="Objective Neuro-Score", showlegend=False)
                st.plotly_chart(fig_dn, use_container_width=True)
            else:
                st.info("No Day/Night data available in the current dataset.")
                
        with col2:
            st.markdown("#### Illuminance Extremes")
            if 'Illuminance_lux' in self.df_spatial.columns:
                df_ill = self.df_spatial.copy()
                q25 = df_ill['Illuminance_lux'].quantile(0.25)
                q75 = df_ill['Illuminance_lux'].quantile(0.75)
                
                def assign_ill(val):
                    if pd.isna(val): return "Unknown"
                    if val <= q25: return "Bottom 25% (Darkest)"
                    if val >= q75: return "Top 25% (Brightest)"
                    return "Middle 50%"
                    
                df_ill['Ill_Bucket'] = df_ill['Illuminance_lux'].apply(assign_ill)
                df_ill_extremes = df_ill[df_ill['Ill_Bucket'].isin(["Bottom 25% (Darkest)", "Top 25% (Brightest)"])]
                
                if not df_ill_extremes.empty:
                    fig_ill = px.box(
                        df_ill_extremes, x="Ill_Bucket", y="NeuroScore",
                        points="all", color="Ill_Bucket",
                        color_discrete_map={"Bottom 25% (Darkest)": "#FF6B8A", "Top 25% (Brightest)": "#2FD4C8"}
                    )
                    style_figure(fig_ill, "Neuro-Score by Illuminance Extremes", height=400)
                    fig_ill.update_layout(xaxis_title="Illuminance Bracket", yaxis_title="Objective Neuro-Score", showlegend=False)
                    st.plotly_chart(fig_ill, use_container_width=True)
                else:
                    st.info("Insufficient variance in Illuminance data to compute quantiles.")
            else:
                st.info("Illuminance_lux column missing from dataset.")

        # -------------------------------------------------------------
        # Phase 3: High-Variance Spatial Triggers
        # -------------------------------------------------------------
        panel_header("High-Variance Spatial Triggers", "Anomalies")
        st.markdown("Rooms where physiological objective arousal deviated the most from subjective reported arousal.")
        
        req_trigger_cols = ['objective_arousal', 'subjective_arousal', 'objective_valence', 'subjective_valence']
        if all(c in self.df_spatial.columns for c in req_trigger_cols):
            df_triggers = self.df_spatial.copy()
            df_triggers['Delta_Arousal_Raw'] = df_triggers['objective_arousal'] - df_triggers['subjective_arousal']
            df_triggers['Delta_Valence_Raw'] = df_triggers['objective_valence'] - df_triggers['subjective_valence']
            
            # Sort by Delta_Arousal_Raw descending
            df_sorted = df_triggers.sort_values(by='Delta_Arousal_Raw', ascending=False).head(10)
            
            room_col = 'Room_ID' if 'Room_ID' in df_sorted.columns else 'Room ID'
            if room_col in df_sorted.columns:
                df_plot = df_sorted.sort_values(by='Delta_Arousal_Raw', ascending=True)
                
                # Task 1: Generate Unique Y-Axis Labels
                if 'Subject_ID' in df_plot.columns:
                    df_plot['Unique_Trial_Label'] = df_plot['Subject_ID'].astype(str) + " - " + df_plot[room_col].astype(str)
                elif 'Trial_ID' in df_plot.columns:
                    df_plot['Unique_Trial_Label'] = "Trial " + df_plot['Trial_ID'].astype(str) + " - " + df_plot[room_col].astype(str)
                else:
                    df_plot['Unique_Trial_Label'] = "Trial " + df_plot.index.astype(str) + " - " + df_plot[room_col].astype(str)
                
                hover_cols = ['Walkable_Floor_Area_m2', 'Illuminance_lux', 'Window_Area_m2', 'Num_Doors']
                actual_hover_cols = [c for c in hover_cols if c in df_plot.columns]
                
                custom_data = df_plot[actual_hover_cols].values if actual_hover_cols else []
                
                ht_sub = "Label: %{y}<br><b>Subjective Arousal</b>: %{x:.2f}<br>---<br>"
                ht_obj = "Label: %{y}<br><b>Objective Arousal</b>: %{x:.2f}<br>---<br>"
                
                for i, col in enumerate(actual_hover_cols):
                    clean_col = col.replace('_', ' ')
                    ht_sub += f"{clean_col}: %{{customdata[{i}]:.1f}}<br>"
                    ht_obj += f"{clean_col}: %{{customdata[{i}]:.1f}}<br>"
                
                ht_sub += "<extra></extra>"
                ht_obj += "<extra></extra>"
                
                fig_dumb = go.Figure()

                for idx, row in df_plot.iterrows():
                    fig_dumb.add_trace(go.Scatter(
                        x=[row['subjective_arousal'], row['objective_arousal']],
                        y=[row['Unique_Trial_Label'], row['Unique_Trial_Label']],
                        mode='lines',
                        line=dict(color='rgba(255,255,255,0.3)', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                fig_dumb.add_trace(go.Scatter(
                    x=df_plot['subjective_arousal'],
                    y=df_plot['Unique_Trial_Label'],
                    mode='markers',
                    name='Subjective Arousal',
                    marker=dict(color='#4287C6', size=12, line=dict(color='rgba(255,255,255,0.8)', width=1)),
                    customdata=custom_data,
                    hovertemplate=ht_sub
                ))

                fig_dumb.add_trace(go.Scatter(
                    x=df_plot['objective_arousal'],
                    y=df_plot['Unique_Trial_Label'],
                    mode='markers',
                    name='Objective Arousal',
                    marker=dict(color='#FF6B8A', size=12, line=dict(color='rgba(255,255,255,0.8)', width=1)),
                    customdata=custom_data,
                    hovertemplate=ht_obj
                ))

                style_figure(fig_dumb, "Spatial Triggers (Δ Arousal)", height=500)
                fig_dumb.update_layout(
                    xaxis_title="Arousal",
                    yaxis_title="Subject & Room",
                    showlegend=True,
                    yaxis=dict(type='category', categoryorder='array', categoryarray=df_plot['Unique_Trial_Label'])
                )
                st.plotly_chart(fig_dumb, use_container_width=True)
            else:
                st.warning("Room identifier missing for Dumbbell Plot.")
        else:
            st.info("Required objective/subjective columns not found for delta calculations.")

        # -------------------------------------------------------------
        # Phase 4: Non-Linear Feature Importance
        # -------------------------------------------------------------
        panel_header("Non-Linear Feature Importance", "Random Forest")
        st.markdown("Evaluating the absolute threshold impact of spatial dimensions on the Objective Neuro-Score.")
        
        if numeric_cols and 'NeuroScore' in self.df_spatial.columns:
            # Prepare data
            df_ml = self.df_spatial[numeric_cols + ['NeuroScore']].dropna()
            if len(df_ml) > 10:
                X = df_ml[numeric_cols]
                y = df_ml['NeuroScore']
                
                # Train Random Forest
                rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
                rf.fit(X, y)
                
                # Extract importances
                importances = rf.feature_importances_
                imp_df = pd.DataFrame({
                    'Feature': numeric_cols,
                    'Importance': importances
                }).sort_values(by='Importance', ascending=True)
                
                fig_rf = px.bar(
                    imp_df, x='Importance', y='Feature', orientation='h',
                    color='Importance', color_continuous_scale="Viridis"
                )
                style_figure(fig_rf, "Random Forest Feature Contributions", height=max(400, len(numeric_cols)*30))
                fig_rf.update_layout(xaxis_title="Relative Importance (Gini)", yaxis_title="Spatial Feature")
                st.plotly_chart(fig_rf, use_container_width=True)
            else:
                st.warning("Not enough clean data samples to train the Random Forest.")
        else:
            st.info("Missing spatial features or target for Random Forest training.")

        panel_header("Parametric Response Heatmap", "3D Surface")
        if 'spatial_model' in st.session_state and st.session_state.spatial_model is not None:
            from src.services.prediction_service import PredictionService
            from src.config import get_config
            model = st.session_state.spatial_model
            feature_names = st.session_state.get('feature_names', [])
            scaler = st.session_state.get('scaler', None)
            
            if feature_names and len(feature_names) > 3:
                available_feats = [f for f in numeric_cols if f in feature_names and f in self.df_spatial.columns]
                
                col1, col2 = st.columns(2)
                with col1:
                    feat_x = st.selectbox("X-Axis Feature", available_feats, index=available_feats.index('Length_m') if 'Length_m' in available_feats else 0, key="surf_x")
                with col2:
                    feat_y = st.selectbox("Y-Axis Feature", available_feats, index=available_feats.index('Window_Area_m2') if 'Window_Area_m2' in available_feats else min(1, len(available_feats)-1), key="surf_y")

                ps = PredictionService(config=get_config(), model=model, feature_names=feature_names, scaler=scaler)
                means = {}
                for f in feature_names:
                    if f in self.df_spatial.columns:
                        means[f] = self.df_spatial[f].mean()
                    else:
                        means[f] = 0.0
                
                if feat_x and feat_y:
                    x_range = np.linspace(self.df_spatial[feat_x].min(), self.df_spatial[feat_x].max(), 20)
                    y_range = np.linspace(self.df_spatial[feat_y].min(), self.df_spatial[feat_y].max(), 20)
                    
                    z_data = np.zeros((20, 20))
                    for i, x_val in enumerate(x_range):
                        for j, y_val in enumerate(y_range):
                            feat_dict = means.copy()
                            feat_dict[feat_x] = x_val
                            feat_dict[feat_y] = y_val
                            res = ps.predict_full(feat_dict)
                            z_data[j, i] = res.neuro_score
                    
                    fig_surf = go.Figure(data=[go.Surface(
                        z=z_data, x=x_range, y=y_range,
                        colorscale='Viridis',
                        colorbar=dict(title='Neuro-Score')
                    )])
                    
                    x_name = feat_x.replace('_m2', ' (m²)').replace('_m', ' (m)').replace('_pct', ' (%)').replace('_lux', ' (lux)').replace('_K', ' (K)')
                    y_name = feat_y.replace('_m2', ' (m²)').replace('_m', ' (m)').replace('_pct', ' (%)').replace('_lux', ' (lux)').replace('_K', ' (K)')
                    
                    style_figure(fig_surf, f"Neuro-Score vs {y_name} & {x_name}", height=600)
                    fig_surf.update_layout(
                        scene=dict(
                            xaxis_title=x_name,
                            yaxis_title=y_name,
                            zaxis_title='Predicted Neuro-Score'
                        ),
                        font=dict(family="'Google Sans Flex'")
                    )
                    st.plotly_chart(fig_surf, use_container_width=True)
                else:
                    st.info("Please select both X and Y features.")
            else:
                st.info("Full feature model required for 3D Surface.")

def render_page():
    vis = SpatialInsightsVis()
    vis.render()
