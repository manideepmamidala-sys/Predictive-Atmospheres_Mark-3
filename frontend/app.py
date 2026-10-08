import streamlit as st
import streamlit.web.cli as stcli
import sys
from pathlib import Path
from PIL import Image

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
from frontend.api_client import get_config

def render_landing_page():
    st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 1rem; color: #E0E0E0; font-family: 'Google Sans Flex', sans-serif;">Predictive Atmospheres</h1>
            <p style="font-size: 1.5rem; color: #B0BEC5; max-width: 800px; margin: 0 auto;">
                A biometric machine learning pipeline mapping the correlation between spatial design parameters and human emotional responses (Valence & Arousal).
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            ### The Biometric Pipeline
            Predictive Atmospheres uses non-invasive biometric sensors (EEG and ECG) to measure human physiological responses to simulated spatial environments. 
            
            By mapping these responses to the Circumplex Model of Affect, we can quantify how architectural parameters like ceiling height, daylight factor, and spatial volume directly impact human emotion.
            
            **Key Methodologies:**
            - Continuous EEG/ECG tracking
            - Immersive VR spatial evaluation
            - Machine Learning (Random Forest) for inverse design optimization
        """)
    
    with col2:
        try:
            img_path = Path(__file__).resolve().parent / "assets" / "IMAGES" / "Affective Fusion" / "Target (Fused).png"
            if img_path.exists():
                st.image(str(img_path), caption="Affective Fusion Mapping", use_column_width=True)
            else:
                st.info("Affective Fusion Graphic placeholder")
        except:
            pass

    st.markdown("---")
    st.markdown("### Research Findings Overview")
    
    c1, c2, c3 = st.columns(3)
    try:
        base_dir = Path(__file__).resolve().parent / "assets" / "IMAGES"
        if (base_dir / "Human Metrics" / "EEG Band Balance.png").exists():
            c1.image(str(base_dir / "Human Metrics" / "EEG Band Balance.png"), caption="EEG Frequency Bands")
        if (base_dir / "Spatial Insights" / "Feature Correlation Matrix.png").exists():
            c2.image(str(base_dir / "Spatial Insights" / "Feature Correlation Matrix.png"), caption="Spatial Correlation")
        if (base_dir / "Demographic Insights" / "Valence Distribution - Gender.png").exists():
            c3.image(str(base_dir / "Demographic Insights" / "Valence Distribution - Gender.png"), caption="Demographic Valence")
    except:
        pass


def main():
    st.set_page_config(
        page_title="Predictive Atmospheres",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    import plotly.io as pio
    current_default = pio.templates.default or "plotly_dark"
    pio.templates[current_default].layout.font.family = "'Google Sans Flex'"
    pio.templates.default = current_default
    
    apply_global_theme()
    
    st.session_state.trained = True 
    
    tabs = st.tabs([
        "Landing Page",
        "Design Studio",
        "Human Metrics",
        "Spatial Insights",
        "Emotion Landscape",
        "Affective Fusion",
        "Demographic Insights",
        "Environmental Impacts",
        "System Architecture",
        "Model Training"
    ])
    
    with tabs[0]:
        render_landing_page()
    with tabs[1]:
        design_studio.render_page(None)
    with tabs[2]:
        human_metrics.render_page()
    with tabs[3]:
        spatial_insights.render_page()
    with tabs[4]:
        emotion_landscape.render_page(None)
    with tabs[5]:
        affective_fusion.render_page()
    with tabs[6]:
        demographic_insights.render_page()
    with tabs[7]:
        environmental_impacts.render_page()
    with tabs[8]:
        system_architecture.render_system_architecture()
    with tabs[9]:
        model_training.render_page(None)


if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
