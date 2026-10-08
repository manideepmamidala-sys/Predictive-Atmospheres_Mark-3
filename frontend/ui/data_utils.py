import streamlit as st
import pandas as pd
from frontend.api_client import get_fusion_data

def load_parquet_data() -> pd.DataFrame:
    df = get_fusion_data()
    if df is None or df.empty:
        st.markdown(
            f'<div style="background-color: #0A2240; border: 1px solid #FFC107; padding: 1.5rem; color: #FFC107; border-radius: 8px;">'
            "<strong>Error Boundary:</strong> Backend API is unavailable or fusion data is missing. Please check API connection.</div>",
            unsafe_allow_html=True
        )
        st.stop()
    return df
