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
    emotion_landscape,
    affective_fusion,
    demographic_insights,
    environmental_impacts,
    system_architecture,
    model_training
)
from frontend.ui.theme import apply_global_theme, render_hero
from src.config import get_config

def main():
    st.set_page_config(
        page_title="Predictive Atmospheres",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    import plotly.io as pio
    # Force global font for all Plotly charts to preserve styling in static PNG downloads
    current_default = pio.templates.default or "plotly_dark"
    pio.templates[current_default].layout.font.family = "'Google Sans Flex'"
    pio.templates.default = current_default
    
    apply_global_theme()
    
    config = get_config()
    
    st.session_state.trained = True # Assume backend API is running
    
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
            "Affective Fusion",
            "Demographic Insights",
            "Environmental Impacts",
            "System Architecture",
            "Model Training"
        ],
        label_visibility="collapsed",
    )

    if mode == "Model Training":
        model_training.render_page(None)
    elif mode == "System Architecture":
        system_architecture.render_system_architecture()
    elif mode == "Design Studio":
        design_studio.render_page(None)
    elif mode == "Human Metrics":
        human_metrics.render_page()
    elif mode == "Spatial Insights":
        spatial_insights.render_page()
    elif mode == "Emotion Landscape":
        emotion_landscape.render_page(None)

    elif mode == "Affective Fusion":
        affective_fusion.render_page()
    elif mode == "Demographic Insights":
        demographic_insights.render_page()
    elif mode == "Environmental Impacts":
        environmental_impacts.render_page()

if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
