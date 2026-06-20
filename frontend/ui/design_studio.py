import streamlit as st
import numpy as np
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import requests

from src.utils.rendering import render_3d_room, render_2d_affective_map
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

def optimize_room(services: Optional[Any] = None):
    """Callback to run inverse design optimization."""
    if not st.session_state.trained:
        st.error("Training in progress...")
        return

    target = st.session_state.target_score

    try:
        response = requests.post("http://127.0.0.1:8000/optimize", json={"target_neuro_score": target}, timeout=15)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.ConnectionError:
        st.error("Backend API is offline. Please run 'uvicorn api:app --reload' in your terminal.")
        return
    except Exception as e:
        st.error(f"Optimization failed: {e}")
        return

    st.session_state["L"] = float(result["length"])
    st.session_state["W"] = float(result["width"])
    safe_height = max(3.0, float(result["height"]))
    st.session_state["H"] = safe_height
    st.session_state["last_opt_neuro_score"] = float(result["neuro_score"])
    
    # Sync all secondary expanded sliders from the full_features dictionary
    for ui_key in ['num_doors', 'door_area', 'num_windows', 'window_area', 
                   'daylight_factor', 'illuminance', 'cct', 'walkable_floor']:
        if ui_key in result["full_features"]:
            st.session_state[ui_key] = float(result["full_features"][ui_key])


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
    features['Height_m'] = float(st.session_state.get('H', max(3.0, float(config.room.default_height))))

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
    condition = st.session_state.get('condition', 'Day')
    is_day = (condition == 'Day')
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
    selected_space = st.session_state.get('space_type', 'Unspecified')
    for name in feature_names:
        if name.startswith('Type_of_Space_'):
            space_label = name.replace('Type_of_Space_', '')
            if selected_space == "Unspecified":
                features[name] = 0.0
            else:
                features[name] = 1.0 if space_label == selected_space else 0.0

    return features


def render_page(services: Optional[Any] = None):
    st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 100%; }
        div[data-testid="stMetric"] { margin-bottom: -15px; }
        .stSlider { padding-bottom: 0px; margin-bottom: -10px; }
        div[data-testid="stExpander"] { border: none; }
        /* Compress plotly charts slightly */
        .js-plotly-plot { margin-top: -15px; }
        /* Shrink standard metric values */
        div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    </style>
    """, unsafe_allow_html=True)

    col_title, col_metrics = st.columns([1.5, 1.5])
    with col_title:
        st.title("Interactive Design Studio")
        st.caption("Shape room geometry and architectural parameters, inspect predicted emotional response, and use inverse optimization to co-design toward target affect.")

    # Backend is now purely API, so we don't set models locally.

    config = get_config()
    pred_v = None
    pred_a = None
    pred_va = None
    ref_centroids = config.emotion.centroids
    emotion_weights = {}

    col_controls, col_visuals = st.columns([1, 2], gap="medium")

    with col_controls:
        input_left, input_right = st.columns(2)
        
        with input_left:
            st.markdown("### Geometry")
            if "L" not in st.session_state: st.session_state["L"] = config.room.default_length
            if "W" not in st.session_state: st.session_state["W"] = config.room.default_width
            if "H" not in st.session_state: st.session_state["H"] = max(3.0, float(config.room.default_height))

            length = st.slider("Length (m)", config.room.min_length, config.room.max_length, key="L")
            width = st.slider("Width (m)", config.room.min_width, config.room.max_width, key="W")
            height = st.slider("Height (m)", 3.0, float(max(3.0, config.room.max_height)), key="H")

            prev_l = st.session_state.get("prev_L", length)
            prev_w = st.session_state.get("prev_W", width)
            prev_h = st.session_state.get("prev_H", height)
            resized = (length != prev_l) or (width != prev_w) or (height != prev_h)

            footprint = float(length * width)
            wall_area = float(2 * (length + width) * height)

            if resized:
                st.session_state["door_area"] = min(2.0, float(0.20 * wall_area))
                st.session_state["window_area"] = min(1.5, float(0.60 * wall_area))
                st.session_state["walkable_floor"] = float(0.30 * footprint)

            st.markdown("### Openings")
            st.slider("Number of Doors", 0.0, 10.0, 1.0, step=1.0, key="num_doors")
            max_door_area = float(0.20 * wall_area)
            if "door_area" not in st.session_state: st.session_state["door_area"] = min(2.0, max_door_area)
            door_area = st.slider("Door Area (m²)", 0.0, max_door_area, key="door_area")
            
            st.slider("Number of Windows", 0.0, 30.0, 2.0, step=1.0, key="num_windows")
            max_window_area = float(0.60 * wall_area)
            if "window_area" not in st.session_state: st.session_state["window_area"] = min(1.5, max_window_area)
            window_area = st.slider("Window Area (m²)", 0.0, max_window_area, key="window_area")

        with input_right:
            st.markdown("### Daylight")
            st.slider("Daylight Factor (%)", 0.0, 20.0, 2.0, key="daylight_factor")
            st.slider("Illuminance (lux)", 0.0, 2000.0, 300.0, key="illuminance")
            st.slider("CCT (Kelvin)", 2000.0, 10000.0, 4000.0, key="cct")

            st.markdown("### Space Details")
            max_walkable_area = float(footprint)
            if "walkable_floor" not in st.session_state: st.session_state["walkable_floor"] = float(0.30 * footprint)
            walkable_floor = st.slider("Walkable Floor Area (m²)", 0.0, max_walkable_area, key="walkable_floor")
            
            st.radio("Lighting Condition", ["Day", "Night"], horizontal=True, key="condition")
            st.selectbox("Type of Space", ["Unspecified"] + config.spatial_features.space_types, index=0, key="space_type")

            st.markdown("### AI Co-Design")
            st.slider("Target Neuro-Score", 0.0, 1.0, 0.8, key="target_score")
            button_disabled = (window_area + door_area) > wall_area
            st.button("Auto-Design Room", on_click=optimize_room, args=(services,), use_container_width=True, disabled=button_disabled)



    # --- INFERENCE ---
    confidence = None
    pred_result = None
    if st.session_state.get('trained', False):
        features = _collect_full_features(config)
        
        try:
            response = requests.post("http://127.0.0.1:8000/predict", json=features, timeout=5)
            response.raise_for_status()
            pred_result = response.json()
            
            pred_v = pred_result["Valence"]
            pred_a = pred_result["Arousal"]
            pred_va = np.array([pred_v, pred_a], dtype=float)
            confidence = pred_result.get("Confidence")
            emotion_weights = pred_result.get("EmotionWeights", {})
        except requests.exceptions.ConnectionError:
            st.error("Backend API is offline. Please run 'uvicorn api:app --reload' in your terminal.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

    # --- TOP METRICS ---
    with col_metrics:
        if pred_v is not None and pred_a is not None and pred_result is not None:
            neuro_score = float(pred_result["NeuroScore"])
            m1, m2, m3, m4, m5 = st.columns([1.2, 1, 1, 1, 1.2])
            neuro_score_value = f"{neuro_score:.2f}"
            m1.markdown(f"""
                <div style="line-height: 1.2; margin-top: -8px;">
                    <span style="font-size: 0.9rem; color: #A0AAB2;">Predicted Neuro-Score</span><br>
                    <span style="font-size: 2.8rem; font-weight: 700; color: #FAFAFA;">{neuro_score_value}</span>
                </div>
            """, unsafe_allow_html=True)
            m2.metric("Valence", f"{pred_v:.2f}")
            m3.metric("Arousal", f"{pred_a:.2f}")
            if confidence is not None:
                m4.metric("Confidence", f"{confidence:.1f}%")
            else:
                m4.metric("Confidence", "N/A")
            m5.metric("Atmospheric Label", _atmosphere_label(pred_v, config))
            
            if "last_opt_neuro_score" in st.session_state:
                st.success(f"Optimized to Neuro-Score: {st.session_state.last_opt_neuro_score:.2f}")
                del st.session_state["last_opt_neuro_score"]


    # --- VISUALS ---
    with col_visuals:
        fig = render_3d_room(length, width, height, pred_v)
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        tab_map, tab_profile, tab_alignment = st.tabs(["Affective Map", "Emotion Profile", "Reference Alignment"])

        with tab_map:
            if pred_v is not None and pred_a is not None:
                fig_vad_map = render_2d_affective_map(pred_v, pred_a, ref_centroids)
                fig_vad_map.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_vad_map, use_container_width=True)
            else:
                st.info("Affective map will appear after model initialization.")
                
        with tab_profile:
            if pred_va is not None and emotion_weights:
                fig_profile = _emotion_profile_chart(emotion_weights)
                fig_profile.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_profile, use_container_width=True)
            else:
                st.info("Emotion profile will appear after model initialization.")

        with tab_alignment:
            if pred_v is not None and pred_a is not None and ref_centroids:
                fig_distance = _centroid_distance_chart(pred_v, pred_a, ref_centroids)
                fig_distance.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_distance, use_container_width=True)
            else:
                st.info("Reference alignment chart will appear after model initialization.")

    st.session_state["prev_L"] = length
    st.session_state["prev_W"] = width
    st.session_state["prev_H"] = height
    st.session_state["prev_W"] = width
