import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import scipy.signal
from src.data.preprocessing import analyze_ecg, analyze_eeg_bands
from frontend.ui.base_visualization import BaseVisualization
from src.config import get_config
from frontend.ui.theme import style_figure, panel_header
from frontend.ui.data_utils import load_parquet_data

config = get_config()
DATA_DIR = config.paths.data_dir

class HumanMetricsVis(BaseVisualization):
    def __init__(self):
        super().__init__(
            title="Population Biometric Analytics",
            description="Aggregated EEG and ECG analysis across all experiments to characterize baseline physiological response patterns."
        )

    def load_data(self):
        self.df_metadata = load_parquet_data()
        
        # Deduplicate on EEG_Filename so we don't compute the same file twice (since 1 file can be mapped to multiple rooms in Exp 01/02)
        self.unique_sessions = self.df_metadata.drop_duplicates(subset=['EEG_Filename']).copy()
        
        if len(self.unique_sessions) == 0:
            raise FileNotFoundError("No recording files found in parquet metadata.")

    def process_data(self):
        with st.spinner(f"Analyzing {len(self.unique_sessions)} unique biometric sessions..."):
            all_metrics = []

            eeg_psd_sum = None
            ecg_psd_sum = None
            psd_count = 0
            freqs = None

            for _, row in self.unique_sessions.iterrows():
                f = row['EEG_Filename']
                exp_id = row.get('experiment_id', 1)
                subject_id = row['Subject_ID']
                
                if pd.isna(f) or not str(f).endswith('.csv'):
                    continue
                    
                # Format experiment folder name
                exp_folder = f"experiment_{int(exp_id):02d}"
                file_path = os.path.join(DATA_DIR, 'raw', exp_folder, str(f))
                
                if not os.path.exists(file_path):
                    continue

                try:
                    df = pd.read_csv(file_path)
                    fs = config.eeg.sample_rate

                    s1, f1, pxx1 = analyze_eeg_bands(df['Channel1'].values, fs)
                    s2, f2, pxx2 = analyze_eeg_bands(df['Channel2'].values, fs)

                    avg_pxx_eeg = (pxx1 + pxx2) / 2
                    avg_delta = (s1['Delta'] + s2['Delta'])/2
                    avg_alpha = (s1['Alpha'] + s2['Alpha'])/2
                    avg_beta = (s1['Beta'] + s2['Beta'])/2
                    ratio_ba = (s1['Beta/Alpha'] + s2['Beta/Alpha'])/2

                    ecg_stats, _, _ = analyze_ecg(df['Channel3'].values, fs)
                    f_ecg, pxx_ecg = scipy.signal.welch(df['Channel3'].values, fs=fs, nperseg=fs*2)

                    if eeg_psd_sum is None:
                        eeg_psd_sum = np.zeros_like(avg_pxx_eeg)
                        ecg_psd_sum = np.zeros_like(pxx_ecg)
                        freqs = f1

                    if len(avg_pxx_eeg) == len(eeg_psd_sum):
                        eeg_psd_sum += avg_pxx_eeg
                        ecg_psd_sum += pxx_ecg
                        psd_count += 1

                    # Recover Day/Night from parquet
                    day_night = "Unspecified"
                    if row.get('Day_or_Night_Day', 0) == 1: day_night = "Day"
                    elif row.get('Day_or_Night_Night', 0) == 1: day_night = "Night"

                    all_metrics.append({
                        "Session": f,
                        "Subject": subject_id,
                        "Experiment": f"Exp {int(exp_id):02d}",
                        "Day/Night": day_night,
                        "Age": row.get('age', None),
                        "Delta Power": avg_delta,
                        "Alpha Power": avg_alpha,
                        "Beta Power": avg_beta,
                        "Beta/Alpha (Stress)": ratio_ba,
                        "Heart Rate (BPM)": ecg_stats['BPM'],
                        "HRV (ms)": ecg_stats['HRV']
                    })
                except Exception as e:
                    continue

            if not all_metrics:
                raise ValueError("Could not process any valid files.")

            self.df_res = pd.DataFrame(all_metrics)
            self.psd_count = psd_count
            self.freqs = freqs
            if psd_count > 0:
                self.avg_eeg_psd = eeg_psd_sum / psd_count
                self.avg_ecg_psd = ecg_psd_sum / psd_count

    def build_charts(self):
        experiments = sorted(self.df_res['Experiment'].unique())
        if len(experiments) > 1:
            selected_exp = st.multiselect(
                "Filter by Experiment",
                experiments,
                default=experiments,
                key="human_metrics_exp_filter"
            )
            df_filtered = self.df_res[self.df_res['Experiment'].isin(selected_exp)]
        else:
            df_filtered = self.df_res

        panel_header("Key Population Indicators", "Population Overview")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Avg Stress Ratio", f"{df_filtered['Beta/Alpha (Stress)'].mean():.2f}")
        c2.metric("Avg Heart Rate", f"{df_filtered['Heart Rate (BPM)'].mean():.1f} BPM")
        c3.metric("Avg HRV", f"{df_filtered['HRV (ms)'].mean():.1f} ms")
        c4.metric("Total Sessions", len(df_filtered))
        c5.metric("Experiments", len(df_filtered['Experiment'].unique()))

        col_plots1, col_plots2 = st.columns(2)

        with col_plots1:
            st.markdown("#### Stress Distribution")
            fig_stress = go.Figure()
            for exp in sorted(df_filtered['Experiment'].unique()):
                exp_data = df_filtered[df_filtered['Experiment'] == exp]
                fig_stress.add_trace(
                    go.Violin(
                        y=exp_data["Beta/Alpha (Stress)"],
                        box_visible=True,
                        meanline_visible=True,
                        points="all",
                        pointpos=0,
                        name=exp,
                        opacity=0.8,
                    )
                )
            style_figure(fig_stress, "Beta/Alpha Population Spread by Experiment", height=320)
            fig_stress.update_layout(yaxis_title="Beta/Alpha", xaxis_title="")
            st.plotly_chart(fig_stress, width="stretch")

        with col_plots2:
            st.markdown("#### Heart Rate vs HRV")
            fig_hr = go.Figure()
            exp_colors = {"Exp 01": "#8B7CFF", "Exp 02": "#2FD4C8", "Exp 03": "#FF6B8A"}
            for exp in sorted(df_filtered['Experiment'].unique()):
                exp_data = df_filtered[df_filtered['Experiment'] == exp]
                fig_hr.add_trace(go.Scatter(
                    x=exp_data["Heart Rate (BPM)"],
                    y=exp_data["HRV (ms)"],
                    mode="markers",
                    text=exp_data["Session"],
                    name=exp,
                    marker=dict(
                        size=12,
                        color=exp_colors.get(exp, "#4287C6"),
                        line=dict(color="rgba(9,11,18,0.8)", width=1),
                    ),
                    hovertemplate="Session: %{text}<br>HR: %{x:.2f} BPM<br>HRV: %{y:.2f} ms<extra></extra>",
                ))
            style_figure(fig_hr, "Autonomic Regulation Map", height=320)
            fig_hr.update_layout(xaxis_title="Heart Rate (BPM)", yaxis_title="HRV (ms)")
            st.plotly_chart(fig_hr, width="stretch")

        if 'Day/Night' in df_filtered.columns and df_filtered['Day/Night'].nunique() > 1:
            panel_header("Day/Night Condition Breakdown", "Condition Analysis")
            dn_col1, dn_col2 = st.columns(2)

            with dn_col1:
                dn_stress = df_filtered.groupby('Day/Night')['Beta/Alpha (Stress)'].mean()
                fig_dn = go.Figure(go.Bar(
                    x=dn_stress.index,
                    y=dn_stress.values,
                    marker=dict(color=['#2FD4C8', '#8B7CFF', '#FF6B8A'][:len(dn_stress)]),
                    text=[f"{v:.2f}" for v in dn_stress.values],
                    textposition='outside',
                ))
                style_figure(fig_dn, "Average Stress by Condition", height=300)
                st.plotly_chart(fig_dn, width="stretch")

            with dn_col2:
                dn_hr = df_filtered.groupby('Day/Night')['Heart Rate (BPM)'].mean()
                fig_dn2 = go.Figure(go.Bar(
                    x=dn_hr.index,
                    y=dn_hr.values,
                    marker=dict(color=['#2FD4C8', '#8B7CFF', '#FF6B8A'][:len(dn_hr)]),
                    text=[f"{v:.1f}" for v in dn_hr.values],
                    textposition='outside',
                ))
                style_figure(fig_dn2, "Average Heart Rate by Condition", height=300)
                st.plotly_chart(fig_dn2, width="stretch")

        panel_header("EEG Band Balance", "Spectral Summary")
        band_means = {
            "Delta": float(df_filtered["Delta Power"].mean()),
            "Alpha": float(df_filtered["Alpha Power"].mean()),
            "Beta": float(df_filtered["Beta Power"].mean()),
        }
        fig_bands = go.Figure(
            go.Bar(
                x=list(band_means.keys()),
                y=list(band_means.values()),
                marker=dict(color=["#6E7BD8", "#2FD4C8", "#FF6B8A"]),
                text=[f"{v:.2f}" for v in band_means.values()],
                textposition="outside",
            )
        )
        style_figure(fig_bands, "Average EEG Spectral Power", height=320)
        fig_bands.update_layout(xaxis_title="Band", yaxis_title="Power")
        st.plotly_chart(fig_bands, width="stretch")

        if hasattr(self, 'psd_count') and self.psd_count > 0:
            mask_eeg = self.freqs < 60
            mask_ecg = self.freqs < 10

            panel_header("Population Average Signals (Frequency Domain)", "Signal Envelopes")
            col_avg1, col_avg2 = st.columns(2)

            with col_avg1:
                st.markdown("**Average EEG Spectrum**")
                fig_avg_eeg = go.Figure()
                fig_avg_eeg.add_trace(
                    go.Scatter(
                        x=self.freqs[mask_eeg],
                        y=self.avg_eeg_psd[mask_eeg],
                        fill='tozeroy',
                        line=dict(color='#8B7CFF', width=2),
                        fillcolor='rgba(139,124,255,0.22)',
                        name='EEG Power',
                    )
                )
                fig_avg_eeg.add_vrect(x0=8, x1=12, fillcolor="rgba(47,212,200,0.12)", line_width=0)
                fig_avg_eeg.add_vrect(x0=13, x1=30, fillcolor="rgba(255,107,138,0.10)", line_width=0)
                fig_avg_eeg.add_annotation(x=10, y=float(np.max(self.avg_eeg_psd[mask_eeg])) * 0.92, text="Alpha", showarrow=False)
                fig_avg_eeg.add_annotation(x=20, y=float(np.max(self.avg_eeg_psd[mask_eeg])) * 0.82, text="Beta", showarrow=False)
                style_figure(fig_avg_eeg, "Brain Spectral Envelope", height=300)
                fig_avg_eeg.update_layout(xaxis_title="Frequency (Hz)", yaxis_title="Power")
                st.plotly_chart(fig_avg_eeg, width="stretch")

            with col_avg2:
                st.markdown("**Average ECG Spectrum**")
                fig_avg_ecg = go.Figure()
                fig_avg_ecg.add_trace(
                    go.Scatter(
                        x=self.freqs[mask_ecg],
                        y=self.avg_ecg_psd[mask_ecg],
                        fill='tozeroy',
                        line=dict(color='#2FD4C8', width=2),
                        fillcolor='rgba(47,212,200,0.20)',
                        name='ECG Power',
                    )
                )
                style_figure(fig_avg_ecg, "Cardiac Spectral Envelope", height=300)
                fig_avg_ecg.update_layout(xaxis_title="Frequency (Hz)", yaxis_title="Power")
                st.plotly_chart(fig_avg_ecg, width="stretch")

        with st.expander("View Aggregated Session Table"):
            st.dataframe(df_filtered)

def render_page():
    vis = HumanMetricsVis()
    vis.render()
