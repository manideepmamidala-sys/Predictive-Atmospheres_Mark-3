import os
import requests
import pandas as pd
import streamlit as st

def get_api_url() -> str:
    """Get the base URL for the backend API."""
    if "API_URL" in st.secrets:
        return st.secrets["API_URL"].rstrip("/")
    return os.environ.get("API_URL", "http://localhost:8000").rstrip("/")

@st.cache_data(ttl=3600)
def get_fusion_data() -> pd.DataFrame:
    """Fetch fusion data from the API and return as a DataFrame."""
    try:
        response = requests.get(f"{get_api_url()}/data/fusion", timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to fetch fusion data from API: {e}")
        # Fallback to local file if API is not available during dev
        from pathlib import Path
        data_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "fusion_analysis.parquet"
        if data_path.exists():
            return pd.read_parquet(data_path)
        return pd.DataFrame()

def predict(features: dict) -> dict:
    """Get prediction from the backend model."""
    try:
        response = requests.post(f"{get_api_url()}/predict", json=features, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Prediction API error: {e}")
        return None

def optimize(target_neuro_score: float) -> dict:
    """Get inverse optimization from the backend model."""
    try:
        response = requests.post(
            f"{get_api_url()}/inverse-optimize", 
            json={"target_neuro_score": target_neuro_score},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Optimization API error: {e}")
        return None

def check_health() -> bool:
    """Check if the backend API is healthy."""
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=5)
        return response.status_code == 200
    except:
        return False
