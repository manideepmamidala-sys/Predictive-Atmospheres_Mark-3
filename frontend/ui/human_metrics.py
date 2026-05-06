import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import scipy.signal
from src.data.preprocessing import analyze_ecg, analyze_eeg_bands
from src.data.experiment_registry import discover_experiments
from frontend.ui.base_visualization import BaseVisualization
from src.config import get_config
from frontend.ui.theme import style_figure, panel_header

config = get_config()
DATA_DIR = config.paths.data_dir

class HumanMetricsVis(BaseVisualization):
    def __init__(self):
        super().__init__(
            title="Population Biometric Analytics",
            description="Aggregated EEG and ECG analysis across all experiments to characterize baseline physiological response patterns."
        )

    def load_data(self):
        experiments = discover_experiments()
        self.experiment_data = {}
        self.all_files = []

        for exp in experiments:
            data_dir = exp.raw_dir
            if not os.path.exists(data_dir):
                continue
            files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and f.startswith('Subj_')]
            if files:
                self.experiment_data[exp.name] = {
                    'dir': data_dir,
                    'files': files,
                    'biometric_csv': exp.biometric_csv,
                }
                for f in files:
                    self.all_files.append((exp.name, data_dir, f))

        if not self.all_files:
            # Fallback to legacy experiment_01 directory
            legacy_dir = os.path.join(DATA_DIR, 'raw', 'experiment_01')
            if os.path.exists(legacy_dir):
                files = [f for f in os.listdir(legacy_dir) if f.endswith('.csv') and f.startswith('Subj_')]
                for f in files:
                    self.all_files.append(('experiment_01', legacy_dir, f))

        if not self.all_files:
            raise FileNotFoundError("No recording files (Subj_*.csv) found in any experiment directory.")

    def process_data(self):
        with st.spinner(f"Analyzing {len(self.all_files)} biometric sessions across {len(self.experiment_data)} experiments..."):
            all_metrics = []

            eeg_psd_sum = None
            ecg_psd_sum = None
            psd_count = 0
            freqs = None

            for exp_name, data_dir, f in self.all_files:
                try:
                    parts = f.replace('.csv', '').split('-')
                    subject_id = parts[0].split('_')[1] if len(parts) > 0 and '_' in parts[0] else "Unknown"
                    timestamp = f"{parts[1]}-{parts[2]}" if len(parts) >= 3 else "Unknown"
                    df = pd.read_csv(os.path.join(data_dir, f))
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

                    # Try to load Day/Night condition from biometric metadata
                    day_night = "Unknown"
                    if exp_name in self.experiment_data:
                        try:
                            bio_csv = self.experiment_data[exp_name]['biometric_csv']
                            bio_df = pd.read_csv(bio_csv)
                            if 'Day or Night' in bio_df.columns and 'Subject_ID' in bio_df.columns:
                                match = bio_df[bio_df['Subject_ID'].astype(str).str.contains(subject_id, na=False)]
                                if len(match) > 0:
                                    day_night = str(match.iloc[0].get('Day or Night', 'Unknown'))
                        except Exception:
                            pass

                    all_metrics.append({
                        "Session": f,
                        "Subject": subject_id,
                        "Experiment": exp_name,
                        "Day/Night": day_night,
                        "Timestamp": timestamp,
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
        # Experiment filter
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
            stress_vals = df_filtered["Beta/Alpha (Stress)"]
            fig_hr = go.Figure()
            # Color by experiment
            exp_colors = {"experiment_01": "#8B7CFF", "experiment_02": "#2FD4C8"}
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
                        color=exp_colors.get(exp, "#FF6B8A"),
                        line=dict(color="rgba(9,11,18,0.8)", width=1),
                    ),
                    hovertemplate="Session: %{text}<br>HR: %{x:.2f} BPM<br>HRV: %{y:.2f} ms<extra></extra>",
                ))
            style_figure(fig_hr, "Autonomic Regulation Map", height=320)
            fig_hr.update_layout(xaxis_title="Heart Rate (BPM)", yaxis_title="HRV (ms)")
            st.plotly_chart(fig_hr, width="stretch")

        # Day/Night breakdown
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
