"""
Model Training UI Page
Displays training convergence, architecture info, and paper-aligned evaluation metrics.
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from src.models.train import train_models_logic
from typing import Optional
from src.services.container import ServiceContainer
from frontend.ui.theme import render_hero, style_figure, panel_header


def render_page(services: Optional[ServiceContainer] = None):
    render_hero(
        "Model Training Pipeline",
        "Monitor convergence behavior and retrain architectures when your spatial or biometric dataset evolves.",
        kicker="Model Development",
        compact=True,
    )

    st.info("Models train automatically on startup. Retraining here updates the active predictor for all pages.")

    model_type = st.selectbox(
        "Model Architecture",
        ['PyTorch FFNN', 'PyTorch MLP', 'Random Forest', 'Ridge Regression'],
        index=0 if st.session_state.get('model_type', 'PyTorch FFNN') == 'PyTorch FFNN' else 1,
    )

    feature_mode = st.selectbox(
        "Feature Mode",
        ['full', 'baseline'],
        index=0,
        help="'full' uses all spatial features (20+), 'baseline' uses only Length/Width/Height.",
    )

    if st.button(f"Retrain {model_type} ({feature_mode})", use_container_width=True):
        result = train_models_logic(model_type=model_type, feature_mode=feature_mode)
        if services is not None and 'spatial_model' in st.session_state:
            services.set_model(st.session_state.spatial_model)
            services.set_feature_config(
                feature_names=st.session_state.get('feature_names', []),
                scaler=st.session_state.get('scaler', None),
            )
        st.success("Retraining Complete!")

    # Architecture summary
    panel_header("Architecture Summary", "Model Info")
    model_t = st.session_state.get('model_type', 'Unknown')
    feat_mode = st.session_state.get('feature_mode', 'Unknown')
    feat_names = st.session_state.get('feature_names', [])

    c_info1, c_info2, c_info3 = st.columns(3)
    c_info1.metric("Architecture", model_t)
    c_info2.metric("Feature Mode", feat_mode)
    c_info3.metric("Feature Count", len(feat_names))

    if feat_names:
        with st.expander("Feature List", expanded=False):
            for i, name in enumerate(feat_names, 1):
                st.text(f"{i}. {name}")

    # Evaluation metrics
    if 'eval_metrics' in st.session_state and st.session_state.eval_metrics:
        panel_header("Evaluation Metrics", "Performance")
        metrics = st.session_state.eval_metrics
        col_t, col_v = st.columns(2)
        with col_t:
            st.markdown("**Training Set**")
            st.metric("MAE", f"{metrics.get('Train_MAE', 0):.4f}")
            st.metric("RMSE", f"{metrics.get('Train_RMSE', 0):.4f}")
            st.metric("R²", f"{metrics.get('Train_R2', 0):.4f}")
        with col_v:
            st.markdown("**Validation Set**")
            st.metric("MAE", f"{metrics.get('Val_MAE', 0):.4f}")
            st.metric("RMSE", f"{metrics.get('Val_RMSE', 0):.4f}")
            st.metric("R²", f"{metrics.get('Val_R2', 0):.4f}")

    panel_header("Learning Dynamics", "Convergence")
    st.caption("Error descent profile for spatial-to-affect model optimization.")

    if 'loss_history' in st.session_state and st.session_state.loss_history:
        history = np.array(st.session_state.loss_history, dtype=float)
        epochs = np.arange(1, len(history) + 1)
        smooth_window = min(10, max(3, len(history) // 8))
        kernel = np.ones(smooth_window) / smooth_window
        smooth_loss = np.convolve(history, kernel, mode='same')

        fig_loss = go.Figure()
        fig_loss.add_trace(
            go.Scatter(
                x=epochs,
                y=history,
                mode='lines',
                name='Raw Loss',
                line=dict(color='rgba(139,124,255,0.45)', width=2),
            )
        )
        fig_loss.add_trace(
            go.Scatter(
                x=epochs,
                y=smooth_loss,
                mode='lines',
                name='Smoothed Loss',
                line=dict(color='#2FD4C8', width=3),
            )
        )
        style_figure(fig_loss, 'Training Convergence', height=420)
        fig_loss.update_layout(xaxis_title='Epoch', yaxis_title='MSE Loss')

        c_main, c_side = st.columns([2.3, 1], gap='large')
        with c_main:
            st.plotly_chart(fig_loss, width='stretch')

        with c_side:
            st.metric('Epochs', len(history))
            st.metric('Initial Loss', f"{history[0]:.4f}")
            st.metric('Final Loss', f"{history[-1]:.4f}")
            gain = ((history[0] - history[-1]) / max(history[0], 1e-8)) * 100
            st.metric('Reduction', f"{gain:.1f}%")
            if st.session_state.get('converged', False):
                st.success("Model converged ✓")
            if 'final_lr' in st.session_state:
                st.caption(f"Final LR: {st.session_state.final_lr:.6f}")

        if len(history) > 2:
            delta = np.diff(history)
            fig_delta = go.Figure(
                go.Scatter(
                    x=np.arange(2, len(history) + 1),
                    y=delta,
                    mode='lines',
                    line=dict(color='#FF6B8A', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(255,107,138,0.18)',
                    name='Loss Change',
                )
            )
            style_figure(fig_delta, 'Epoch-to-Epoch Loss Change', height=300)
            fig_delta.update_layout(xaxis_title='Epoch', yaxis_title='Δ Loss')
            st.plotly_chart(fig_delta, width='stretch')

        with st.expander('Learning Process Interpretation', expanded=False):
            st.markdown(
                """
                - Initialization starts with non-optimized parameters and higher prediction error.
                - Forward pass estimates affective output from spatial feature vectors.
                - Loss quantifies mismatch between predictions and measured affective targets.
                - Backpropagation updates model parameters to reduce error iteratively.
                - A descending and stabilizing curve indicates convergence toward a useful mapping.
                - The FFNN architecture uses batch normalization and dropout for regularization.
                """
            )

    else:
        st.warning("Training history is not available yet. Run retraining to generate convergence diagnostics.")
