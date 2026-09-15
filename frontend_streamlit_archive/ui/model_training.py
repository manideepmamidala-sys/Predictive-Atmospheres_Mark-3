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


def plot_model_performance(adapter):
    import torch
    
    # 1. Try to get it from the adapter
    if hasattr(adapter, 'framework'):
        framework = adapter.framework
        raw_model = adapter.model
    # 2. Fallback: If it's a raw PyTorch Module
    elif isinstance(adapter, torch.nn.Module):
        framework = 'pytorch'
        raw_model = adapter
    # 3. Fallback: If it's a raw Scikit-Learn Model
    elif hasattr(adapter, 'predict') and not isinstance(adapter, torch.nn.Module):
        framework = 'sklearn'
        raw_model = adapter
    else:
        framework = 'unknown'
        raw_model = adapter

    if framework == 'pytorch':
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
                    name='Train Loss',
                    line=dict(color='rgba(139,124,255,0.7)', width=2),
                )
            )
            if 'val_loss_history' in st.session_state and st.session_state.val_loss_history:
                val_history = np.array(st.session_state.val_loss_history, dtype=float)
                fig_loss.add_trace(
                    go.Scatter(
                        x=epochs,
                        y=val_history,
                        mode='lines',
                        name='Val Loss',
                        line=dict(color='#2FD4C8', width=2),
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
    elif framework == 'sklearn':
        panel_header("Feature Importance / Coefficients", "Model Weights")
        feat_names = st.session_state.get('feature_names', [])
        if not feat_names:
            return
            
        from typing import Any
        pipeline: Any = raw_model
        if not hasattr(pipeline, 'steps'):
            st.info("Feature importance is not available for this model architecture.")
            return
        reg = pipeline.steps[-1][1]
        
        if hasattr(reg.estimators_[0], 'feature_importances_'):
            importances = np.mean([est.feature_importances_ for est in reg.estimators_], axis=0)
            title = "Feature Importance (Random Forest)"
        elif hasattr(reg.estimators_[0], 'coef_'):
            importances = np.mean(np.abs([est.coef_ for est in reg.estimators_]), axis=0)
            title = "Absolute Coefficients (Ridge Regression)"
        else:
            st.info("No feature importance available for this model type.")
            return
            
        import pandas as pd
        df_imp = pd.DataFrame({"Feature": feat_names, "Importance": importances})
        df_imp.sort_values(by="Importance", ascending=True, inplace=True)
            
        fig = go.Figure(go.Bar(
            x=df_imp["Importance"],
            y=df_imp["Feature"],
            orientation='h',
            marker=dict(color='#8B7CFF')
        ))
        style_figure(fig, title, height=max(300, len(feat_names)*30))
        st.plotly_chart(fig, width='stretch')


def render_page(services: Optional[ServiceContainer] = None):
    render_hero(
        "Model Training Pipeline",
        "Monitor convergence behavior and retrain architectures when your spatial or biometric dataset evolves.",
        kicker="Model Development",
        compact=True,
    )

    st.info("Models train automatically on startup. Retraining here updates the active predictor for all pages.")

    st.markdown("### Model Architecture Selection")
    
    prod_model_type = st.radio(
        "Production Models",
        ['Random Forest', 'Ridge Regression'],
        index=0 if st.session_state.get('model_type', 'Random Forest') == 'Random Forest' else 1,
    )
    
    with st.expander("Legacy Models (Evaluation Only)"):
        use_legacy = st.checkbox("Enable Legacy Model Training")
        leg_model_type = st.radio(
            "Legacy Neural Networks",
            ['PyTorch FFNN', 'PyTorch MLP'],
            index=0
        )
        
    model_type = leg_model_type if use_legacy else prod_model_type

    if st.button(f"Retrain {model_type} (Full Features)", use_container_width=True, icon=":material/arrow_forward:"):
        result = train_models_logic(model_type=model_type)
        if services is not None and 'spatial_model' in st.session_state:
            services.set_model(st.session_state.spatial_model)
            services.set_feature_config(
                feature_names=st.session_state.get('feature_names', []),
                scaler=st.session_state.get('scaler', None),
            )
        st.success("Retraining Complete!")

    panel_header("Architecture Summary", "Model Info")
    model_t = st.session_state.get('model_type', 'Unknown')
    feat_names = st.session_state.get('feature_names', [])

    c_info1, c_info3 = st.columns(2)
    c_info1.metric("Architecture", model_t)
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

    if 'spatial_model' in st.session_state:
        plot_model_performance(st.session_state.spatial_model)

    if 'parity_df' in st.session_state and st.session_state.parity_df is not None:
        panel_header("Model Accuracy", "Parity Plot")
        df_parity = st.session_state.parity_df
        fig_parity = go.Figure()
        fig_parity.add_trace(go.Scatter(
            x=df_parity['Actual_Valence'],
            y=df_parity['Predicted_Valence'],
            mode='markers',
            name='Valence',
            marker=dict(color='#2FD4C8', size=6, opacity=0.7)
        ))
        fig_parity.add_trace(go.Scatter(
            x=df_parity['Actual_Arousal'],
            y=df_parity['Predicted_Arousal'],
            mode='markers',
            name='Arousal',
            marker=dict(color='#FF6B8A', size=6, opacity=0.7)
        ))
        min_val = min(df_parity.min().min(), -1.0)
        max_val = max(df_parity.max().max(), 1.0)
        fig_parity.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Ideal (45°)',
            line=dict(color='white', dash='dash', width=1)
        ))
        style_figure(fig_parity, "Actual vs Predicted (Validation Set)", height=450)
        fig_parity.update_layout(xaxis_title="Actual Target", yaxis_title="Model Prediction")
        st.plotly_chart(fig_parity, width='stretch')

    else:
        st.warning("Training history is not available yet. Run retraining to generate convergence diagnostics.")


