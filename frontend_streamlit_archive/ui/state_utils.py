# Utility functions for Streamlit UI state handling

"""State utilities for extracting independent spatial features from
Streamlit's ``st.session_state``.

These helpers centralise the logic that collects only INDEPENDENT features.
Derived features (ratios, areas, volumes) are computed by the backend
in ``src.models.train._build_features`` and ``src.services.prediction_service``.

UDI, sDA, and ASE are permanently purged and never collected.
"""

from __future__ import annotations

from typing import Dict
import streamlit as st
from src.config import get_config



