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


def get_current_features_from_state(config) -> Dict[str, float]:
    """Collect independent spatial features from ``st.session_state``.

    Derived features (L:W Ratio, Floor Area, Wall Area, Volume,
    Door/Wall Ratio, Window/Wall Ratio, Walkable/Floor Ratio) are
    NOT included — the backend computes them.
    """
    features: Dict[str, float] = {}

    # Core geometry
    features["Length (meter)"] = float(st.session_state.get("L", config.room.default_length))
    features["Width (meter)"] = float(st.session_state.get("W", config.room.default_width))
    features["Height (meter)"] = float(st.session_state.get("H", config.room.default_height))

    # Openings (independent only)
    features["Number of Door"] = float(st.session_state.get("num_doors", 1.0))
    features["Door Area (sq.meter)"] = float(st.session_state.get("door_area", 1.8))
    features["Number of Windows"] = float(st.session_state.get("num_windows", 2.0))
    features["Window Area (sq.meter)"] = float(st.session_state.get("window_area", 5.0))

    # Daylight (UDI, sDA, ASE permanently purged)
    features["Daylight Factor (%)"] = float(st.session_state.get("daylight_factor", 2.0))
    features["Illuminance (lux)"] = float(st.session_state.get("illuminance", 300.0))
    features["Correlated Color Temperature (Kelvin)"] = float(st.session_state.get("cct", 4000.0))

    # Walkable Floor Area
    features["Walkable Floor Area (sq.meter)"] = float(st.session_state.get("walkable_floor", 60.0))

    # Experiment condition (Day/Night) – one-hot encoded
    is_day = st.session_state.get("is_day", True)
    feature_names = st.session_state.get("feature_names", [])
    for name in feature_names:
        if name.startswith("Day or Night_"):
            if name == "Day or Night_Day":
                features[name] = 1.0 if is_day else 0.0
            elif name == "Day or Night_Night":
                features[name] = 0.0 if is_day else 1.0
            else:
                features[name] = 0.0

    # Type of Space – one-hot encoded
    selected_space = st.session_state.get("space_type", "Living Room")
    for name in feature_names:
        if name.startswith("Type of Space_"):
            space_label = name.replace("Type of Space_", "")
            features[name] = 1.0 if space_label == selected_space else 0.0

    return features
