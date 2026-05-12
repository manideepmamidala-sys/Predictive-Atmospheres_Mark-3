import streamlit as st
import pandas as pd
from pathlib import Path

def load_parquet_data() -> pd.DataFrame:
    data_path = Path("data/processed/fusion_analysis.parquet")
    if not data_path.exists():
        st.markdown(
            f'<div style="background-color: #0A2240; border: 1px solid #FFC107; padding: 1.5rem; color: #FFC107; border-radius: 8px;">'
            "<strong>Error Boundary:</strong> fusion_analysis.parquet is missing. Please run the backend training pipeline first.</div>",
            unsafe_allow_html=True
        )
        st.stop()
    return pd.read_parquet(data_path)
