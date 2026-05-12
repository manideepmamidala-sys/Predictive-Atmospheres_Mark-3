import streamlit as st
import numpy as np
import torch
import plotly.graph_objects as go
from typing import Optional, Dict
from src.utils.rendering import render_3d_room, render_2d_affective_map
from src.services.optimization_service import OptimizationService
from src.services.prediction_service import PredictionService
from src.services.container import ServiceContainer
from src.config import get_config
from frontend.ui.theme import render_hero, style_figure, panel_header

# Consistent color palette for 13 emotions
EMOTION_COLORS = {
    "Happiness": "#2FD4C8",
    "Surprise": "#3FBBFF",
    "Pride": "#8B7CFF",
    "Love": "#B88CFF",
    "Anger": "#FF6B8A",
    "Fear": "#F08AA2",
    "Anxiety": "#FF8B74",
    "Disgust": "#B05C89",
    "Sad": "#6E7BD8",
    "Guilt": "#92A1FF",
    "Regard": "#7BB5FF",
    "Satisfaction": "#4ED9C4",
    "WarmHeartedness": "#6DEAB6",
}

def optimize_room(services: Optional[ServiceContainer] = None):
    """Callback to run inverse design optimization."""
    if not st.session_state.trained:
        st.error("Training in progress...")
        return

    target = st.session_state.target_score

    if services is not None:
        optimizer = services.optimization_service
    else:
        optimizer = OptimizationService(
            model=st.session_state.spatial_model,
            feature_names=st.session_state.get('feature_names', []),
            scaler=st.session_state.get('scaler', None)
        )
    result = optimizer.optimize_for_target(target_score=float(target), method="differential_evolution")

    st.session_state["L"] = float(result.length)
    st.session_state["W"] = float(result.width)
    st.session_state["H"] = float(result.height)
    opt_valence = float(result.predicted_valence)
    st.session_state["last_opt_neuro_score"] = (opt_valence + 1.0) / 2.0


def _emotion_profile_chart(emotion_weights: dict) -> go.Figure:
    items = sorted(emotion_weights.items(), key=lambda x: x[1], reverse=True)
    top_items = items[:8]
    labels = [name for name, _ in top_items][::-1]
    values = [weight * 100 for _, weight in top_items][::-1]
    colors = [EMOTION_COLORS.get(label, "#8A93AA") for label in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
        )
    )
    style_figure(fig, "Dominant Emotional Components", height=340)
    fig.update_layout(xaxis_title="Contribution (%)", yaxis_title="Emotion")
    return fig


def _centroid_distance_chart(pred_v: float, pred_a: float, centroids: dict) -> go.Figure:
    items = []
    for name, coords in centroids.items():
        dist = float(np.sqrt((pred_v - coords[0]) ** 2 + (pred_a - coords[1]) ** 2))
        items.append((name, dist))
    items = sorted(items, key=lambda x: x[1])[:8]
    labels = [item[0] for item in items][::-1]
    values = [item[1] for item in items][::-1]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color="rgba(139,124,255,0.80)"),
            hovertemplate="%{y}<br>Distance: %{x:.3f}<extra></extra>",
        )
    )
    style_figure(fig, "Nearest Affective Archetypes", height=340)
    fig.update_layout(xaxis_title="Euclidean Distance in V-A Space", yaxis_title="Reference Emotion")
    return fig


def _atmosphere_label(pred_v: float, config) -> str:
    if pred_v > config.emotion.positive_threshold:
        return "POSITIVE / WELCOMING"
    if pred_v > config.emotion.negative_threshold:
        return "NEUTRAL"
    return "NEGATIVE / STRESSFUL"


def _collect_full_features(config) -> Dict[str, float]:
    """Collect independent spatial features from session state.
    Derived features are NOT collected here — they are computed server-side.
    """
    sf = config.spatial_features
    features: Dict[str, float] = {}

    # Core geometry
    features['Length_m'] = float(st.session_state.get('L', config.room.default_length))
    features['Width_m'] = float(st.session_state.get('W', config.room.default_width))
    features['Height_m'] = float(st.session_state.get('H', config.room.default_height))

    # Openings (independent only — ratios computed server-side)
    features['Num_Doors'] = float(st.session_state.get('num_doors', 1.0))
    features['Door_Area_m2'] = float(st.session_state.get('door_area', 1.8))
    features['Num_Windows'] = float(st.session_state.get('num_windows', 2.0))
    features['Window_Area_m2'] = float(st.session_state.get('window_area', 5.0))

    # Daylight (UDI, sDA, ASE permanently purged)
    features['Daylight_Factor_pct'] = float(st.session_state.get('daylight_factor', 2.0))
    features['Illuminance_lux'] = float(st.session_state.get('illuminance', 300.0))
    features['CCT_K'] = float(st.session_state.get('cct', 4000.0))

    # Walkable Floor Area
    features['Walkable_Floor_Area_m2'] = float(st.session_state.get('walkable_floor', 60.0))

    # Condition (Day/Night) – one-hot encoded
    is_day = st.session_state.get('is_day', True)
    feature_names = st.session_state.get('feature_names', [])
    for name in feature_names:
        if name.startswith('Day_or_Night_'):
            if name == 'Day_or_Night_Day':
                features[name] = 1.0 if is_day else 0.0
            elif name == 'Day_or_Night_Night':
                features[name] = 0.0 if is_day else 1.0
            else:
                features[name] = 0.0

    # Type of Space – one-hot encoded
    selected_space = st.session_state.get('space_type', 'Living Room')
    for name in feature_names:
        if name.startswith('Type_of_Space_'):
            space_label = name.replace('Type_of_Space_', '')
            features[name] = 1.0 if space_label == selected_space else 0.0

    return features


def render_page(services: Optional[ServiceContainer] = None):
    render_hero(
        "Interactive Design Studio",
        "Shape room geometry and architectural parameters, inspect predicted emotional response, and use inverse optimization to co-design toward target affect.",
        kicker="Design + Predict",
        compact=True,
    )

    if services is not None and "spatial_model" in st.session_state and st.session_state.spatial_model is not None:
        services.set_model(st.session_state.spatial_model)

    config = get_config()
    pred_v = None
    pred_a = None
    pred_va = None
    ref_centroids = config.emotion.centroids
    emotion_weights = {}

    col_ctrl, col_viz = st.columns([1.2, 2.8], gap="medium")

    with col_ctrl:
        # ---- Core Geometry ----
        panel_header("Room Geometry", "Inputs")
        if "L" not in st.session_state:
            st.session_state["L"] = config.room.default_length
        if "W" not in st.session_state:
            st.session_state["W"] = config.room.default_width
        if "H" not in st.session_state:
            st.session_state["H"] = config.room.default_height

        length = st.slider("Length (m)", config.room.min_length, config.room.max_length, key="L")
        width = st.slider("Width (m)", config.room.min_width, config.room.max_width, key="W")
        height = st.slider("Height (m)", config.room.min_height, config.room.max_height, key="H")

        footprint = float(length * width)
        volume = float(length * width * height)
        c_geom1, c_geom2 = st.columns(2)
        c_geom1.metric("Footprint", f"{footprint:.1f} m²")
        c_geom2.metric("Volume", f"{volume:.1f} m³")

        # ---- Openings ----
        with st.expander("🚪 Openings", expanded=False):
            st.slider("Number of Doors", 0.0, 10.0, 1.0, step=1.0, key="num_doors")
            st.slider("Door Area (m²)", 0.0, 30.0, 1.8, key="door_area")
            st.slider("Number of Windows", 0.0, 30.0, 2.0, step=1.0, key="num_windows")
            st.slider("Window Area (m²)", 0.0, 250.0, 5.0, key="window_area")

        # ---- Daylight (UDI, sDA, ASE permanently purged) ----
        with st.expander("☀️ Daylight & Lighting", expanded=False):
            st.slider("Daylight Factor (%)", 0.0, 20.0, 2.0, key="daylight_factor")
            st.slider("Illuminance (lux)", 0.0, 2000.0, 300.0, key="illuminance")
            st.slider("CCT (Kelvin)", 2000.0, 10000.0, 4000.0, key="cct")

        # ---- Floor ----
        with st.expander("🏗️ Floor", expanded=False):
            st.slider("Walkable Floor Area (m²)", 0.0, 500.0, 60.0, key="walkable_floor")

        # ---- Condition ----
        with st.expander("🌗 Experiment Condition", expanded=False):
            st.toggle("Day (vs Night)", value=True, key="is_day")
            st.caption("Controls the Day/Night condition under which the model evaluates the space.")

        # ---- Type of Space ----
        with st.expander("🏢 Space Type", expanded=False):
            st.selectbox(
                "Type of Space",
                config.spatial_features.space_types,
                index=1,  # Default: Living Room
                key="space_type",
            )
            st.caption("Categorical variable one-hot encoded before model input.")

        # ---- Optimization ----
        panel_header("AI Co-Design", "Optimization")
        st.caption("Set a target emotional score and run inverse design optimization.")
        st.slider("Target Neuro-Score", 0.0, 1.0, 0.8, key="target_score")
        st.button("Auto-Design Room", on_click=optimize_room, args=(services,), use_container_width=True)

        if "last_opt_neuro_score" in st.session_state:
            st.success(f"Optimized configuration reached Predicted Neuro-Score: {st.session_state.last_opt_neuro_score:.2f}")
            del st.session_state["last_opt_neuro_score"]

        # ---- Model Inference ----
        panel_header("Model Inference", "Live Prediction")

        if st.session_state.get('trained', False):
            features = _collect_full_features(config)
            feature_names = st.session_state.get('feature_names', [])

            if services is not None:
                ref_centroids = services.prediction_service.get_reference_centroids()
                if feature_names and len(feature_names) > 3:
                    pred_result = services.prediction_service.predict_full(features)
                else:
                    pred_result = services.prediction_service.predict(length, width, height)
                pred_v = pred_result.valence
                pred_a = pred_result.arousal
                pred_va = np.array([pred_v, pred_a], dtype=float)
                emotion_weights = pred_result.emotion_weights
            else:
                model = st.session_state.spatial_model
                if model is not None:
                    if feature_names and len(feature_names) > 3:
                        ps = PredictionService(
                            config=config, model=model,
                            feature_names=feature_names,
                            scaler=st.session_state.get('scaler'),
                        )
                        pred_result = ps.predict_full(features)
                        pred_v = pred_result.valence
                        pred_a = pred_result.arousal
                        pred_va = np.array([pred_v, pred_a], dtype=float)
                        emotion_weights = pred_result.emotion_weights
                    else:
                        input_tensor = torch.tensor([[length, width, height]], dtype=torch.float32)
                        with torch.no_grad():
                            output = model(input_tensor)
                            if isinstance(output, dict):
                                output = output["affective_space"]
                            pred_va = output.detach().cpu().numpy().flatten()
                        pred_v = float(pred_va[0])
                        pred_a = float(pred_va[1])
                        ps = PredictionService(config=config)
                        emotion_weights = ps._compute_emotion_weights(pred_v, pred_a)

            if pred_v is not None:
                neuro_score = (pred_v + 1.0) / 2.0
                st.metric("Predicted Neuro-Score", f"{neuro_score:.2f}", help="0.0 = negative, 1.0 = positive")
                c_val, c_aro = st.columns(2)
                c_val.metric("Valence", f"{pred_v:.2f}")
                c_aro.metric("Arousal", f"{pred_a:.2f}")

                st.caption(f"Atmospheric Label: {_atmosphere_label(pred_v, config)}")


        else:
            st.info("Initializing models...")

    with col_viz:
        fig = render_3d_room(length, width, height, pred_v)
        st.plotly_chart(fig, width="stretch")

        tab_map, tab_profile, tab_reference, tab_features = st.tabs([
            "Affective Map", "Emotion Profile", "Reference Alignment", "Feature Radar"
        ])

        with tab_map:
            if pred_va is not None:
                fig_vad_map = render_2d_affective_map(pred_v, pred_a, ref_centroids)
                st.plotly_chart(fig_vad_map, width="stretch")
            else:
                st.info("Affective map will appear after model initialization.")

        with tab_profile:
            if pred_va is not None and emotion_weights:
                fig_profile = _emotion_profile_chart(emotion_weights)
                st.plotly_chart(fig_profile, width="stretch")
            else:
                st.info("Emotion profile will appear after model initialization.")

        with tab_reference:
            if pred_va is not None and ref_centroids:
                fig_distance = _centroid_distance_chart(pred_v, pred_a, ref_centroids)
                st.plotly_chart(fig_distance, width="stretch")
            else:
                st.info("Reference alignment chart will appear after model initialization.")

        with tab_features:
            if pred_va is not None:
                features = _collect_full_features(config)
                # Show radar chart of current feature values
                display_features = {
                    k: v for k, v in features.items()
                    if not k.startswith('Day_or_Night_') and not k.startswith('Type_of_Space_') and v != 0.0
                }
                # Normalize for radar display
                labels = []
                values = []
                for fname, fval in sorted(display_features.items()):
                    if hasattr(config.spatial_features, fname):
                        fmax = getattr(config.spatial_features, fname)['max']
                        labels.append(fname.replace('_m2', ' (m²)').replace('_m', ' (m)').replace('_pct', ' (%)').replace('_lux', ' (lux)').replace('_K', ' (K)'))
                        values.append(float(fval) / max(fmax, 1e-6))

                if labels:
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=labels + [labels[0]],
                        fill='toself',
                        name='Current Config',
                        line=dict(color='#2FD4C8', width=2),
                        fillcolor='rgba(47,212,200,0.20)',
                    ))
                    style_figure(fig_radar, "Spatial Feature Profile", height=400)
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(range=[0, 1.1], gridcolor="rgba(167,177,203,0.20)"),
                            bgcolor="rgba(17,22,37,0.70)",
                        )
                    )
                    st.plotly_chart(fig_radar, width="stretch")
            else:
                st.info("Feature radar will appear after model initialization.")
