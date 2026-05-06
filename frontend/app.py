import streamlit as st
import streamlit.web.cli as stcli
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from frontend.ui import (
    design_studio,
    human_metrics,
    spatial_insights,
    model_training,
    emotion_landscape,
    design_benchmark,
    affective_fusion_analysis,
)
from frontend.ui.theme import apply_global_theme, render_hero
from src.services import ServiceContainer
from src.config import get_config


@st.cache_resource(show_spinner="Loading ML backend...")
def _load_ml_backend():
    from src.models.architectures import SpatialMLP, SpatialFFNN
    from src.models.train import train_models_logic

    return SpatialMLP, SpatialFFNN, train_models_logic

def main():
    st.set_page_config(
        page_title="Predictive Atmospheres",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_theme()
    render_hero(
        "Emotion-Aware Spatial Intelligence",
        "Machine learning framework to infer human emotional states from architectural space and embed affective intelligence into design decisions.",
        kicker="Neuro-Architectural Design Platform",
        compact=True,
    )

    try:
        SpatialMLP, SpatialFFNN, train_models_logic = _load_ml_backend()
    except KeyboardInterrupt:
        st.error("PyTorch initialization was interrupted. Please run the app again and allow model backend loading to finish.")
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load ML backend: {exc}")
        st.stop()
    
    # Initialize Session State for Models
    if 'spatial_model' not in st.session_state:
        st.session_state.spatial_model = None
        st.session_state.trained = False
        st.session_state.feature_names = []
        st.session_state.feature_mode = 'full'
        st.session_state.model_type = 'PyTorch FFNN'
        st.session_state.scaler = None

    config = get_config()

    if 'services' not in st.session_state:
        st.session_state.services = ServiceContainer(config=config, model=st.session_state.spatial_model)
    else:
        st.session_state.services.set_model(st.session_state.spatial_model)

    # --- Auto-Train on Startup ---
    if not st.session_state.trained:
        result = train_models_logic()
        st.session_state.services.set_model(st.session_state.spatial_model)
        # Update services with feature config + scaler
        st.session_state.services.set_feature_config(
            feature_names=st.session_state.get('feature_names', []),
            scaler=st.session_state.get('scaler', None),
        )
    
    # Sidebar Navigation
    st.sidebar.markdown("### Predictive Atmospheres")
    st.sidebar.caption("Workspace Navigation")
    mode = st.sidebar.radio(
        "Select workspace section",
        [
            "Design Studio",
            "Human Metrics",
            "Spatial Insights",
            "Emotion Landscape",
            "Design Benchmark",
            "Affective Fusion",
            "Model Training",
        ],
        label_visibility="collapsed",
    )

    if mode == "Model Training":
        model_training.render_page(st.session_state.services)
    elif mode == "Design Studio":
        design_studio.render_page(st.session_state.services)
    elif mode == "Human Metrics":
        human_metrics.render_page()
    elif mode == "Spatial Insights":
        spatial_insights.render_page()
    elif mode == "Emotion Landscape":
        emotion_landscape.render_page(st.session_state.services)
    elif mode == "Design Benchmark":
        design_benchmark.render_page(st.session_state.services)
    elif mode == "Affective Fusion":
        affective_fusion_analysis.render_page()

if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
